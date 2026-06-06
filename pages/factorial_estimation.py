# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo==0.23.9",
#     "altair==6.2.1",
# ]
# ///
import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    import altair as alt
    import math

    return alt, math


@app.cell
def _(math):
    MAX_N = 500
    MEMORIZED_PRIMES = (2, 3, 5, 7)
    STIRLING_FORMULA = r"N\left(\log_{10}(N) - \log_{10}(e)\right) + 1"

    def true_log10_factorial(n):
        return math.lgamma(n + 1) / math.log(10)

    def direct_stirling_log10(n):
        if n <= 1:
            return 0.0
        return n * (math.log10(n) - math.log10(math.e)) + 1

    def is_easy_anchor(n):
        if n < 1:
            return False
        remaining = n
        for prime in MEMORIZED_PRIMES:
            while remaining % prime == 0:
                remaining //= prime
        return remaining == 1

    EASY_ANCHORS = [n for n in range(1, MAX_N + 1) if is_easy_anchor(n)]
    ROUND_EASY_ANCHORS = [n for n in EASY_ANCHORS if n % 5 == 0]

    def nearest_anchor(n):
        return min(ROUND_EASY_ANCHORS, key=lambda anchor: (abs(anchor - n), anchor))

    def prime_factorization(n):
        if n == 1:
            return {1: 1}

        remaining = n
        factors = {}
        divisor = 2
        while divisor * divisor <= remaining:
            while remaining % divisor == 0:
                factors[divisor] = factors.get(divisor, 0) + 1
                remaining //= divisor
            divisor += 1
        if remaining > 1:
            factors[remaining] = factors.get(remaining, 0) + 1
        return factors

    def factorization_latex(n):
        factors = prime_factorization(n)
        if factors == {1: 1}:
            return "1"
        parts = []
        for factor, power in factors.items():
            if power == 1:
                parts.append(str(factor))
            else:
                parts.append(rf"{factor}^{{{power}}}")
        return r" \times ".join(parts)

    def easy_log_terms_latex(n):
        factors = prime_factorization(n)
        if factors == {1: 1}:
            return "0"

        terms = []
        for factor, power in factors.items():
            coefficient = "" if power == 1 else str(power)
            if factor == 5:
                base_term = r"\left(1 - \log_{10}(2)\right)"
            else:
                base_term = rf"\log_{{10}}({factor})"
            terms.append(f"{coefficient}{base_term}")
        return " + ".join(terms)

    def memorized_constants(decimal_places):
        return {
            "log2": round(math.log10(2), decimal_places),
            "log3": round(math.log10(3), decimal_places),
            "log7": round(math.log10(7), decimal_places),
            "stirling": round(math.log10(math.e), decimal_places),
        }

    def estimated_log10_easy_number(n, constants):
        if n == 1:
            return 0.0

        factors = prime_factorization(n)
        if any(prime not in MEMORIZED_PRIMES for prime in factors):
            raise ValueError(f"{n} is not an easy anchor")

        log5 = 1 - constants["log2"]
        return (
            factors.get(2, 0) * constants["log2"]
            + factors.get(3, 0) * constants["log3"]
            + factors.get(5, 0) * log5
            + factors.get(7, 0) * constants["log7"]
        )

    def anchored_mental_log10_factorial(n, decimal_places):
        anchor = nearest_anchor(n)
        constants = memorized_constants(decimal_places)
        anchor_log = estimated_log10_easy_number(anchor, constants)

        if anchor <= 1:
            anchor_factorial_log = 0.0
        else:
            anchor_factorial_log = anchor * (anchor_log - constants["stirling"]) + 1

        correction_log = (n - anchor) * anchor_log
        return {
            "anchor": anchor,
            "anchor_log": anchor_log,
            "anchor_factorial_log": anchor_factorial_log,
            "correction_log": correction_log,
            "estimate": anchor_factorial_log + correction_log,
            "constants": constants,
        }

    def scientific_notation_from_log10(log10_value):
        if log10_value == 0:
            return "1"
        exponent = math.floor(log10_value)
        mantissa = 10 ** (log10_value - exponent)
        return f"{mantissa:.3g} × 10^{exponent}"

    def trim_decimal(value, max_decimal_places=3):
        return f"{value:.{max_decimal_places}f}".rstrip("0").rstrip(".")

    def chart_rows(
        decimal_places,
        visible_methods,
    ):
        rows = []
        for n in range(1, MAX_N + 1):
            true_log = true_log10_factorial(n)
            candidates = {
                "True log₁₀(N!)": true_log,
                "Direct Stirling + 1": direct_stirling_log10(n),
                "Anchored mental estimate": anchored_mental_log10_factorial(
                    n, decimal_places
                )["estimate"],
            }
            for method, log10_value in candidates.items():
                if method in visible_methods:
                    rows.append(
                        {
                            "N": n,
                            "method": method,
                            "log10_value": log10_value,
                            "exponent_error": log10_value - true_log,
                        }
                    )
        return rows

    def precision_summary_rows():
        rows = []
        for decimal_places in range(1, 6):
            errors = []
            for n in range(1, MAX_N + 1):
                estimate = anchored_mental_log10_factorial(n, decimal_places)["estimate"]
                error = estimate - true_log10_factorial(n)
                errors.append(abs(error))

            rows.extend(
                [
                    {
                        "decimal_places": decimal_places,
                        "metric": "Mean absolute exponent error",
                        "value": sum(errors) / len(errors),
                    },
                    {
                        "decimal_places": decimal_places,
                        "metric": "Worst absolute exponent error",
                        "value": max(errors),
                    },
                ]
            )
        return rows

    def precision_heatmap_rows():
        rows = []
        for decimal_places in range(1, 6):
            for n in range(1, MAX_N + 1):
                estimate = anchored_mental_log10_factorial(n, decimal_places)["estimate"]
                rows.append(
                    {
                        "N": n,
                        "decimal_places": decimal_places,
                        "absolute_error": abs(estimate - true_log10_factorial(n)),
                    }
                )
        return rows

    return (
        STIRLING_FORMULA,
        anchored_mental_log10_factorial,
        chart_rows,
        direct_stirling_log10,
        easy_log_terms_latex,
        factorization_latex,
        memorized_constants,
        precision_heatmap_rows,
        precision_summary_rows,
        scientific_notation_from_log10,
        trim_decimal,
        true_log10_factorial,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Approximating factorials in your head

    Being able to quickly approximate the order of magnitude of factorials is, if nothing else, a fun party trick. It could come in handy when thinking about permutations like the number of possible orders of a deck of cards, or the number of ways people could be seated at an event.

    ## The method, by rote

    Here is the method for approximating the order of magnitude of $N!$, without much explanation. The approximations are tuned for $N$ up to about 100, and the end goal is to find the approximate order of magnitude: $N! \approx 10^{\text{<something>}}$.

    Memorize these logarithm values:

    $$
    \begin{aligned}
    \log_{10}(2) &\approx 0.30 \\
    \log_{10}(3) &\approx 0.48 \\
    \log_{10}(7) &\approx 0.85
    \end{aligned}
    $$

    The values above will be used to work out all the other logarithms we'll need, by combining them these log rules:

    $$
    \begin{aligned}
    \log_{10}(x^p \times y^q) &= p\log_{10}(x) + q\log_{10}(y), \\
    \log_{10}(10x) &= 1 + \log_{10}(x), \\
    \log_{10}(5) &= 1 - \log_{10}(2) \text{ (i.e. $\log_{10}(5)$ does not need to be memorized).}
    \end{aligned}
    $$

    Then follow these steps to approximate $N!$:

    1. Pick an "anchor" value, $A$, near to $N$, which is a multiple of 10 or 5 and whose prime factors only include 2, 3, 5 and 7 (matching the memorized logarithm values).
    2. Approximate $\log_{10}(A)$ by breaking $A$ into the product of its prime factors, then apply log rules until reaching something which only contains the logarithms of 2, 3 and 7, which can be substituted for their approximate values.

    3. Approximate $\log_{10}(A!)$ using an approximation $\tilde f(A)\approx\log_{10}(A!)$ based on the Stirling formula. Here is where $A$ being a multiple of 5 or 10 is useful for keeping the mental arithmetic simple.

    $$
    \tilde f(A) = A\left(\log_{10}(A) - 0.43\right) + 1
    $$

    4. To get back to $N!$ from $A!$ (assuming $N > A$) we'll use another approximation, $\log_{10}(A) \approx \log_{10}(A+1) \approx \log_{10}(A+2) \cdots \approx \log_{10}(N)$, so:

    $$
    \begin{aligned}
    \log_{10}(N!) &= \log_{10}\Bigl(A! \times \overbrace{(A+1)(A+2)\cdots(N)}^{(N-A)\text{ terms}} \Bigr) \\
    &\approx \log_{10}(A!) + (N-A)\log_{10}(A)
    \end{aligned}
    $$

    So, all in all, the approximation is:

    $$
    \log_{10}(N!) \approx A\left(\log_{10}(A) - 0.43\right) + 1 + (N-A)\log_{10}(A)
    $$

    Note that this could be simplified to $N\log_{10}(A) - 0.43A + 1$, but in practice these first two terms involve trickier multiplication than the unsimplified version above.

    ## A worked example following the rote method

    For $52!$:

    1. Choose the anchor $A=50$, which is a multiple of ten with prime decomposition $2 \times 5^2$ so it satisfies the constraints on picking an anchor.
    2. Find $\log_{10}(50) = 1 + \log_{10}(5) = 1 + 1 - \log_{10}(2) \approx 2 - 0.3 = 1.7$
    3. Subtract the constant: $1.7 - 0.43 = 1.27$
    4. Multiply by $A$ and add 1: $50 \times 1.27 + 1 = 64.5$
    5. Get back up to $52!$ approx. by adding $64.5 + 2\log_{10}50 \approx 64.5 + 3.4 = 67.9$

    So we have the approximate order of magnitude, $52! \approx 10^{68}$. The true value is roughly $8.07 \times 10^{67}$ so this method has found the nearest power of 10 correctly.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Estimating logarithms

    The Stirling approximation involves calculating logarithms, so to able to estimate factorials with this approximation, we'll need to be able to mentally estimate logarithms as well.

    One way to calculate a logarithm is to break a number up into its prime factors and then sum the logs of those prime factors, for example:

    $$
    \log_{10}(52) = \log_{10}(13 \times 2 \times 2) = \log_{10}(13) + \log_{10}(2) + \log_{10}(2)
    $$

    With this approach, it would be possible to estimate the log of any integer up to $N$ by memorizing estimates of all of the prime factors less $N$.

    This is easier than needing to memorizing the logarithms of every integer up to $N$, but for $N=100$, this would require memorizing logarithms of all primes up to 100, of which there are 25! (Exclamation mark, not factorial.) That's too many logarithms to remember. I certainly won't be doing that.

    But there is a neat way to reduce the amount of logarithms to memorize. Given an estimate for a factorial, $(N-1)!$, it is easy to estimate other nearby factorials like $N!$ as $N! = (N-1)! \times N$. With this, we can avoid calculating awkward logarithms by picking a nearby number which factorizes into primes we've memorized the logarithm of.

    Let's work with the logarithms of 2, 3, 5 and 7. For example, to estimate $52!$ which had a 13 in its prime factorization, we could instead start by estimating $50!$ which factorizes into our chosen set of primes, and then get back $52! = 50! \times 51 \times 52$ afterwards.

    This gives us 3 logarithms to remember.
    """)
    return


@app.function
def readable_chart(chart):
    return (
        chart.configure_axis(
            labelFontSize=14,
            titleFontSize=16,
            labelAngle=0,
        )
        .configure_legend(
            labelFontSize=14,
            titleFontSize=15,
            symbolSize=120,
        )
        .configure_header(
            labelFontSize=14,
            titleFontSize=15,
        )
        .configure_title(fontSize=17)
        .configure_view(strokeWidth=0)
    )


@app.cell(hide_code=True)
def _(mo):
    selected_n = mo.ui.slider(
        start=1,
        stop=500,
        step=1,
        value=52,
        label="N",
    )
    decimal_places = mo.ui.slider(
        start=1,
        stop=5,
        step=1,
        value=2,
        label="Decimal places memorized",
    )
    visible_methods = mo.ui.multiselect(
        options=[
            "True log₁₀(N!)",
            "Direct Stirling + 1",
            "Anchored mental estimate",
        ],
        value=[
            "True log₁₀(N!)",
            "Direct Stirling + 1",
            "Anchored mental estimate",
        ],
        label="Series",
    )

    mo.vstack([selected_n, decimal_places, visible_methods])
    return decimal_places, selected_n, visible_methods


@app.cell(hide_code=True)
def _(
    STIRLING_FORMULA,
    anchored_mental_log10_factorial,
    decimal_places,
    direct_stirling_log10,
    easy_log_terms_latex,
    factorization_latex,
    memorized_constants,
    mo,
    scientific_notation_from_log10,
    selected_n,
    trim_decimal,
    true_log10_factorial,
):
    n = selected_n.value
    places = decimal_places.value
    true_log = true_log10_factorial(n)
    direct_log = direct_stirling_log10(n)
    mental = anchored_mental_log10_factorial(n, places)
    anchor = mental["anchor"]
    distance = n - anchor
    constants = memorized_constants(places)

    constant_rows = [
        rf"- $\log_{{10}}(2) \approx {constants['log2']:.{places}f}$",
        rf"- $\log_{{10}}(3) \approx {constants['log3']:.{places}f}$",
        rf"- $\log_{{10}}(7) \approx {constants['log7']:.{places}f}$",
        rf"- $\log_{{10}}(e) \approx {constants['stirling']:.{places}f}$",
    ]
    constant_list = "\n".join(constant_rows)

    if anchor <= 1:
        anchor_factorial_steps = r"""
    \[
    \log_{10}(1!) = 0
    \]
    """
    else:
        base_anchor_factorial_log = anchor * (
            mental["anchor_log"] - constants["stirling"]
        ) + 1
        anchor_factorial_steps = rf"""
    \[
    \log_{{10}}({anchor}!)
    \approx {anchor}\left({mental["anchor_log"]:.{places}f} - {constants["stirling"]:.{places}f}\right) + 1
    = {trim_decimal(base_anchor_factorial_log)}
    \]
    """

    correction_count = abs(distance)
    if correction_count == 0:
        correction_phrase = "make no correction because the target is the anchor"
    elif correction_count == 1:
        correction_phrase = (
            f"multiply by approximately {anchor}"
            if distance > 0
            else f"divide by approximately {anchor}"
        )
    else:
        correction_phrase = (
            f"multiply by approximately {anchor}^{correction_count}"
            if distance > 0
            else f"divide by approximately {anchor}^{correction_count}"
        )
    correction_expression = (
        rf"+ {distance} \times {mental['anchor_log']:.{places}f}"
        if distance >= 0
        else rf"- {abs(distance)} \times {mental['anchor_log']:.{places}f}"
    )

    mo.md(
        rf"""
    ## Interactive estimate

    Anchor rule: **nearest easy anchor that is also a multiple of 5**.

    Approximation formula:

    \[
    {STIRLING_FORMULA}
    \]

    ### 1. Choose a round easy anchor

    For **{n}!**, the selected anchor is **{anchor}**.

    \[
    {anchor} = {factorization_latex(anchor)}
    \]

    ### 2. Estimate the anchor's logarithm

    With constants rounded to {places} decimal place{'s' if places != 1 else ''}:

    {constant_list}

    \[
    \log_{{10}}({anchor})
    = {easy_log_terms_latex(anchor)}
    \approx {mental["anchor_log"]:.{places}f}
    \]

    ### 3. Estimate the anchor factorial

    {anchor_factorial_steps}

    So the anchor factorial estimate is:

    \[
    \log_{{10}}({anchor}!) \approx {trim_decimal(mental["anchor_factorial_log"])}
    \]

    ### 4. Correct from the anchor to the target

    The shortcut is to {correction_phrase}, so:

    \[
    \log_{{10}}({n}!) \approx \log_{{10}}({anchor}!) + ({n} - {anchor})\log_{{10}}({anchor})
    \]

    \[
    \log_{{10}}({n}!) \approx {trim_decimal(mental["anchor_factorial_log"])} {correction_expression} = {trim_decimal(mental["estimate"])}
    \]

    ### 5. Compare with the true value

    | Quantity | Value |
    | --- | ---: |
    | True $\log_{{10}}({n}!)$ | {true_log:.3f} |
    | Direct Stirling + 1 $\log_{{10}}({n}!)$ | {direct_log:.3f} |
    | Anchored mental $\log_{{10}}({n}!)$ | {mental["estimate"]:.3f} |
    | Direct Stirling + 1 exponent error | {direct_log - true_log:+.3f} |
    | Anchored mental exponent error | {mental["estimate"] - true_log:+.3f} |
    | True value | {scientific_notation_from_log10(true_log)} |
    | Anchored mental estimate | {scientific_notation_from_log10(mental["estimate"])} |
    """
    )
    return


@app.cell(hide_code=True)
def _(alt, chart_rows, decimal_places, mo, visible_methods):
    estimate_chart = (
        alt.Chart(
            alt.Data(
                values=chart_rows(
                    decimal_places.value,
                    visible_methods.value,
                )
            )
        )
        .mark_line(point=False)
        .encode(
            x=alt.X("N:Q", title="N", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("log10_value:Q", title="log₁₀(N!)"),
            color=alt.Color("method:N", title="Series"),
            tooltip=[
                alt.Tooltip("N:Q", format=".0f"),
                alt.Tooltip("method:N"),
                alt.Tooltip("log10_value:Q", title="log₁₀(N!)", format=".3f"),
                alt.Tooltip(
                    "exponent_error:Q",
                    title="Exponent error",
                    format="+.3f",
                ),
            ],
        )
        .properties(width="container", height=320)
        .interactive()
    )

    mo.vstack(
        [
            mo.md("### Estimated vs true factorial size"),
            readable_chart(estimate_chart),
        ]
    )
    return


@app.cell(hide_code=True)
def _(alt, chart_rows, decimal_places, mo, visible_methods):
    error_rows = [
        row
        for row in chart_rows(
            decimal_places.value,
            visible_methods.value,
        )
        if row["method"] != "True log₁₀(N!)"
    ]

    error_chart = (
        alt.Chart(alt.Data(values=error_rows))
        .mark_line()
        .encode(
            x=alt.X("N:Q", title="N", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("exponent_error:Q", title="Estimated - true log₁₀(N!)"),
            color=alt.Color("method:N", title="Series"),
            tooltip=[
                alt.Tooltip("N:Q", format=".0f"),
                alt.Tooltip("method:N"),
                alt.Tooltip(
                    "exponent_error:Q",
                    title="Exponent error",
                    format="+.3f",
                ),
            ],
        )
        .properties(width="container", height=300)
    )

    tolerance_lines = (
        alt.Chart(
            alt.Data(
                values=[
                    {"error": -2, "label": "-2 powers of ten"},
                    {"error": -1, "label": "-1 power of ten"},
                    {"error": 1, "label": "+1 power of ten"},
                    {"error": 2, "label": "+2 powers of ten"},
                ]
            )
        )
        .mark_rule(strokeDash=[5, 5], opacity=0.45)
        .encode(
            y="error:Q",
            tooltip=["label:N"],
        )
    )

    mo.vstack(
        [
            mo.md("### Exponent error"),
            readable_chart((error_chart + tolerance_lines).interactive()),
        ]
    )
    return


@app.cell(hide_code=True)
def _(alt, mo, precision_heatmap_rows, precision_summary_rows):
    summary_chart = (
        alt.Chart(alt.Data(values=precision_summary_rows()))
        .mark_line(point=True)
        .encode(
            x=alt.X(
                "decimal_places:O",
                title="Decimal places memorized",
                axis=alt.Axis(labelAngle=0),
            ),
            y=alt.Y("value:Q", title="Absolute exponent error"),
            color=alt.Color("metric:N", title="Metric"),
            tooltip=[
                alt.Tooltip("decimal_places:O", title="Decimal places"),
                alt.Tooltip("metric:N"),
                alt.Tooltip("value:Q", title="Error", format=".3f"),
            ],
        )
        .properties(width="container", height=260)
    )

    heatmap = (
        alt.Chart(alt.Data(values=precision_heatmap_rows()))
        .mark_rect()
        .encode(
            x=alt.X(
                "N:O",
                title="N",
                axis=alt.Axis(labelAngle=0, labelOverlap="greedy"),
            ),
            y=alt.Y(
                "decimal_places:O",
                title="Decimal places memorized",
                axis=alt.Axis(labelAngle=0),
            ),
            color=alt.Color(
                "absolute_error:Q",
                title="Absolute exponent error",
                scale=alt.Scale(scheme="viridis"),
            ),
            tooltip=[
                alt.Tooltip("N:O"),
                alt.Tooltip("decimal_places:O", title="Decimal places"),
                alt.Tooltip(
                    "absolute_error:Q",
                    title="Absolute exponent error",
                    format=".3f",
                ),
            ],
        )
        .properties(width="container", height=180)
    )

    mo.vstack(
        [
            mo.md("### How much do extra memorized digits help?"),
            readable_chart(summary_chart),
            readable_chart(heatmap),
        ]
    )
    return


if __name__ == "__main__":
    app.run()
