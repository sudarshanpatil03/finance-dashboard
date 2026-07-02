/*
 * payoff.c — Debt Payoff Engine
 * Implements Avalanche (highest interest first) and Snowball (lowest balance first)
 * Input:  JSON via stdin
 * Output: JSON via stdout
 *
 * Compile: gcc -o payoff payoff.exe payoff.c -lm
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define MAX_DEBTS    50
#define MAX_MONTHS   600   /* 50 years max simulation */
#define MAX_NAME_LEN 100

/* ── Debt struct ─────────────────────────────────────── */
typedef struct {
    char   name[MAX_NAME_LEN];
    double balance;
    double interest_rate;   /* annual % e.g. 18.5 */
    double min_payment;
} Debt;

/* ── Simple JSON parser (no external library needed) ─── */

/* Find a number after a key like "extra_payment": 500 */
double parse_number(const char *json, const char *key) {
    char search[128];
    snprintf(search, sizeof(search), "\"%s\"", key);
    const char *pos = strstr(json, search);
    if (!pos) return 0.0;
    pos = strchr(pos, ':');
    if (!pos) return 0.0;
    return atof(pos + 1);
}

/* Find a string value after a key like "method": "avalanche" */
void parse_string(const char *json, const char *key, char *out, int out_size) {
    char search[128];
    snprintf(search, sizeof(search), "\"%s\"", key);
    const char *pos = strstr(json, search);
    if (!pos) { out[0] = '\0'; return; }
    pos = strchr(pos, ':');
    if (!pos) { out[0] = '\0'; return; }
    /* skip whitespace and quote */
    while (*pos && (*pos == ':' || *pos == ' ' || *pos == '"')) pos++;
    int i = 0;
    while (*pos && *pos != '"' && i < out_size - 1) {
        out[i++] = *pos++;
    }
    out[i] = '\0';
}

/* Parse all debts from the JSON array */
int parse_debts(const char *json, Debt *debts) {
    int count = 0;
    const char *pos = strstr(json, "\"debts\"");
    if (!pos) return 0;
    pos = strchr(pos, '[');
    if (!pos) return 0;
    pos++;

    while (*pos && count < MAX_DEBTS) {
        /* find next '{' */
        pos = strchr(pos, '{');
        if (!pos) break;

        Debt d;
        memset(&d, 0, sizeof(d));

        /* Find end of this debt object */
        const char *obj_end = strchr(pos, '}');
        if (!obj_end) break;

        /* Copy this object for parsing */
        int len = (int)(obj_end - pos) + 1;
        char obj[512];
        if (len >= (int)sizeof(obj)) len = (int)sizeof(obj) - 1;
        strncpy(obj, pos, len);
        obj[len] = '\0';

        parse_string(obj, "name", d.name, MAX_NAME_LEN);
        d.balance       = parse_number(obj, "balance");
        d.interest_rate = parse_number(obj, "interest_rate");
        d.min_payment   = parse_number(obj, "min_payment");

        if (d.balance > 0 && d.interest_rate >= 0 && d.min_payment > 0) {
            debts[count++] = d;
        }

        pos = obj_end + 1;
    }
    return count;
}

/* ── Sort helpers ────────────────────────────────────── */
int cmp_avalanche(const void *a, const void *b) {
    /* Highest interest rate first */
    double diff = ((Debt *)b)->interest_rate - ((Debt *)a)->interest_rate;
    return (diff > 0) ? 1 : (diff < 0) ? -1 : 0;
}

int cmp_snowball(const void *a, const void *b) {
    /* Lowest balance first */
    double diff = ((Debt *)a)->balance - ((Debt *)b)->balance;
    return (diff > 0) ? 1 : (diff < 0) ? -1 : 0;
}

/* ── Month-by-month simulation ───────────────────────── */
int simulate(Debt *debts, int count, double extra_payment,
             double *total_interest_out,
             /* Output: balance of each debt per month */
             double schedule[][MAX_DEBTS], int *months_out)
{
    /* Work on a copy of balances */
    double balances[MAX_DEBTS];
    int    paid_off[MAX_DEBTS];
    for (int i = 0; i < count; i++) {
        balances[i] = debts[i].balance;
        paid_off[i] = 0;
    }

    double total_interest = 0.0;
    int month = 0;

    while (month < MAX_MONTHS) {
        /* Check if all debts are paid off */
        int all_done = 1;
        for (int i = 0; i < count; i++) {
            if (balances[i] > 0.01) { all_done = 0; break; }
        }
        if (all_done) break;

        /* Apply monthly interest and minimum payments */
        double leftover = extra_payment;

        for (int i = 0; i < count; i++) {
            if (balances[i] <= 0.01) {
                balances[i] = 0.0;
                continue;
            }
            /* Monthly interest = annual_rate / 12 / 100 */
            double monthly_rate = debts[i].interest_rate / 12.0 / 100.0;
            double interest     = balances[i] * monthly_rate;
            total_interest += interest;
            balances[i]   += interest;

            /* Pay minimum */
            double payment = debts[i].min_payment;
            if (payment > balances[i]) payment = balances[i];
            balances[i] -= payment;
        }

        /* Apply extra payment to the priority debt (first in sorted order with balance > 0) */
        for (int i = 0; i < count; i++) {
            if (balances[i] > 0.01 && leftover > 0) {
                if (leftover >= balances[i]) {
                    leftover   -= balances[i];
                    balances[i] = 0.0;
                } else {
                    balances[i] -= leftover;
                    leftover     = 0.0;
                }
                break;
            }
        }

        /* Cascade: if a debt is paid off, roll its min_payment into leftover for next priority */
        for (int i = 0; i < count; i++) {
            if (balances[i] <= 0.01 && !paid_off[i]) {
                paid_off[i]  = 1;
                leftover    += debts[i].min_payment;
            }
        }

        /* Record balances for this month */
        for (int i = 0; i < count; i++) {
            schedule[month][i] = balances[i] > 0 ? balances[i] : 0.0;
        }
        month++;
    }

    *total_interest_out = total_interest;
    *months_out         = month;
    return month;
}

/* ── Main ────────────────────────────────────────────── */
int main(void) {
    /* Read all stdin into buffer */
    char input[8192];
    int  total = 0;
    int  c;
    while ((c = getchar()) != EOF && total < (int)sizeof(input) - 1) {
        input[total++] = (char)c;
    }
    input[total] = '\0';

    /* Parse method and extra payment */
    char method[20];
    parse_string(input, "method", method, sizeof(method));
    double extra_payment = parse_number(input, "extra_payment");

    /* Parse debts */
    Debt debts[MAX_DEBTS];
    int  count = parse_debts(input, debts);

    if (count == 0) {
        printf("{\"error\": \"No valid debts found in input\"}\n");
        return 1;
    }

    /* Sort by method */
    if (strcmp(method, "snowball") == 0) {
        qsort(debts, count, sizeof(Debt), cmp_snowball);
    } else {
        /* Default: avalanche */
        qsort(debts, count, sizeof(Debt), cmp_avalanche);
    }

    /* Simulate */
    double schedule[MAX_MONTHS][MAX_DEBTS];
    double total_interest = 0.0;
    int    months         = 0;

    simulate(debts, count, extra_payment, &total_interest, schedule, &months);

    /* ── Output JSON ──────────────────────────────────── */
    printf("{\n");
    printf("  \"method\": \"%s\",\n", (strcmp(method, "snowball") == 0) ? "snowball" : "avalanche");
    printf("  \"months_to_freedom\": %d,\n", months);
    printf("  \"total_interest\": %.2f,\n", total_interest);
    printf("  \"debt_names\": [");
    for (int i = 0; i < count; i++) {
        printf("\"%s\"", debts[i].name);
        if (i < count - 1) printf(", ");
    }
    printf("],\n");

    /* Monthly schedule (balance per debt per month) */
    printf("  \"schedule\": [\n");
    for (int m = 0; m < months; m++) {
        printf("    {\"month\": %d, \"balances\": [", m + 1);
        for (int i = 0; i < count; i++) {
            printf("%.2f", schedule[m][i]);
            if (i < count - 1) printf(", ");
        }
        printf("]}");
        if (m < months - 1) printf(",");
        printf("\n");
    }
    printf("  ]\n");
    printf("}\n");

    return 0;
}
