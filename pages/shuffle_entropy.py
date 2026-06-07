# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo==0.23.9",
#     "altair==6.2.1",
#     "numpy==2.3.5",
# ]
#
# [tool.folio.export]
# slug = "shuffle-entropy"
# show_code = true
# ///

import marimo

__generated_with = "0.23.9"
app = marimo.App(
    width="medium",
    app_title="The fairness of playing card shuffles",
)


@app.cell(hide_code=True)
def _():
    import marimo as mo
    import textwrap

    return mo, textwrap


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # The fairness of playing card shuffles

    For a shuffle to be fair, the order of the cards after the shuffle should not depend on the order of the cards before the shuffle. If someone knew where a card was before the shuffle and then tries to guess where it is after the shuffle, then if the shuffle was fair, they should have no edge over someone else guessing uniformly at random.

    The shuffle must have an element of randomness to achieve this. A deterministic shuffle leaves every card in an exactly known position in the deck so cannot be fair.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Shuffle types

    Here are definitions of a few common types of shuffle.

    ### Riffle

    Take the deck approximately in two halves and interleave the cards from each half with varying numbers of cards at each interleaf.

    ### Box

    Cut the deck approximately into four quarters and reverse the order of these quarters. There should be an element of randomness in the number of cards which go into each quarter - some distribution around 13 cards in each part.

    ### Cut

    As with box, cut the deck approximately in two and reverse their orders.

    ### The standard shuffle in the World Series of Poker

    Riffle, riffle, box, riffle, cut.

    ### Shuffle types as code
    """)
    return


@app.cell(hide_code=True)
def _():
    from collections.abc import Callable
    from math import floor, log
    import altair as alt
    import numpy as np
    from numpy.typing import NDArray

    chart_line_width: float = 2.4

    def chart_config(chart: alt.Chart | alt.LayerChart) -> alt.Chart | alt.LayerChart:
        return (
            chart.configure_axis(labelFontSize=12, titleFontSize=13)
            .configure_legend(labelFontSize=12, titleFontSize=13)
            .configure_title(fontSize=16)
            .configure_view(strokeWidth=0)
        )

    def inset_legend() -> alt.Legend:
        return alt.Legend(
            orient="top-right",
            padding=6,
            fillColor="white",
            strokeColor="#ddd",
        )

    return (
        Callable,
        NDArray,
        alt,
        chart_config,
        chart_line_width,
        floor,
        inset_legend,
        log,
        np,
    )


@app.cell
def _(NDArray, np):
    def riffle(deck: NDArray[np.integer]) -> NDArray[np.integer]:
        result: NDArray[np.float64] = np.random.rand(len(deck))
        result = np.sort(result)
        result = 2 * result % 1
        return deck[np.argsort(result)]

    def box(deck: NDArray[np.integer]) -> NDArray[np.integer]:
        deck_len: int = len(deck)
        n1: int = np.random.binomial(deck_len, 0.25)
        n2: int = np.random.binomial(deck_len - n1, 0.333333) + n1
        n3: int = np.random.binomial(deck_len - n2, 0.5) + n2
        return np.concatenate((deck[n3:], deck[n2:n3], deck[n1:n2], deck[:n1]))

    def cut(deck: NDArray[np.integer]) -> NDArray[np.integer]:
        return np.roll(deck, np.random.binomial(len(deck), 0.5))

    def shuffle(deck: NDArray[np.integer]) -> NDArray[np.integer]:
        return cut(riffle(box(riffle(riffle(deck)))))

    def perfect_shuffle(deck: NDArray[np.integer]) -> NDArray[np.integer]:
        return deck[np.argsort(np.random.rand(len(deck)))]

    return box, cut, perfect_shuffle, riffle, shuffle


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Here's a graphical example of each type of shuffle.
    """)
    return


@app.cell(hide_code=True)
def _(
    Callable,
    NDArray,
    alt,
    box,
    chart_config,
    chart_line_width: float,
    cut,
    mo,
    np,
    perfect_shuffle,
    riffle,
    shuffle,
):
    _deck_size: int = 52
    _deck: NDArray[np.integer] = np.arange(_deck_size)

    shuffle_functions: list[Callable[[NDArray[np.integer]], NDArray[np.integer]]] = [
        cut,
        box,
        riffle,
        shuffle,
        perfect_shuffle,
    ]

    shuffled_decks: list[NDArray[np.integer]] = [
        shuffle_function(_deck) for shuffle_function in shuffle_functions
    ]

    x_labels: list[str] = ["Before", "After"]
    _charts: list[alt.Chart | alt.LayerChart] = []
    for shuffled_deck, shuffle_function in zip(shuffled_decks, shuffle_functions):
        _rows: list[dict[str, int | str]] = []
        for _i in _deck:
            _before_position: int = int(shuffled_deck[_i])
            _rows.append(
                {
                    "card": int(_i),
                    "before_position": _before_position,
                    "label": x_labels[0],
                    "position": _before_position,
                }
            )
            _rows.append(
                {
                    "card": int(_i),
                    "before_position": _before_position,
                    "label": x_labels[1],
                    "position": int(_i),
                }
            )

        _charts.append(
            chart_config(
                alt.Chart(alt.Data(values=_rows), title=shuffle_function.__name__)
                .mark_line(opacity=0.7, strokeWidth=chart_line_width)
                .encode(
                    x=alt.X("label:N", title=None, sort=x_labels),
                    y=alt.Y("position:Q", title="Card position"),
                    color=alt.Color(
                        "before_position:Q",
                        scale=alt.Scale(scheme="magma"),
                        legend=None,
                    ),
                    detail="card:N",
                )
                .properties(width="container", height=204)
            )
        )

    mo.vstack(_charts, align="stretch")
    return


@app.cell(hide_code=True)
def _(mo, textwrap):
    mo.md(textwrap.dedent(r"""
    A large number of shuffles, `num_shuffles`, are simulated using the shuffle defined above. For each shuffle, the final position of each card is kept track of in a `deck_size` $\times$ `deck_size` array, building up a histogram of final positions of each card.
    """))
    return


@app.cell
def _(NDArray, np, shuffle):
    deck_size: int = 52
    deck: NDArray[np.integer] = np.arange(deck_size)

    num_shuffles: int = 30000
    shuffle_weight: float = 1 / num_shuffles

    position_distributions: NDArray[np.float64] = np.zeros([deck_size, deck_size])

    for _i in range(num_shuffles):
        shuffled: NDArray[np.integer] = shuffle(deck)
        for position in range(deck_size):
            position_distributions[shuffled[position]][position] += shuffle_weight
    return deck_size, position_distributions


@app.cell(hide_code=True)
def _(mo, textwrap):
    mo.md(textwrap.dedent(r"""
    Example histograms are shown below for the final position of a card which started at the top of the deck, another card which started in the middle, and one at the bottom.

    When trying to guess where the card on the bottom of the deck ended up, guessing that it's somewhere in the bottom half of the deck will be correct more than half the time because it hasn't been shuffled uniformly. The card which started in the middle of the deck is more uniformly distributed.
    """))
    return


@app.cell
def _(
    alt,
    chart_config,
    chart_line_width: float,
    deck_size: int,
    inset_legend,
    mo,
    position_distributions: "NDArray[np.float64]",
):
    _rows: list[dict[str, float | int | str]] = []
    for card_label, card_index in [("Top", 0), ("Middle", 25), ("Bottom", 51)]:
        for _position, _probability in enumerate(position_distributions[card_index]):
            _rows.append(
                {
                    "card": card_label,
                    "position": _position,
                    "probability": _probability,
                }
            )

    distribution_chart = (
        chart_config(
            alt.Chart(alt.Data(values=_rows))
            .mark_line(strokeWidth=chart_line_width)
            .encode(
                x=alt.X("position:Q", title="Final card position"),
                y=alt.Y("probability:Q", title="Probability"),
                color=alt.Color("card:N", title=None, legend=inset_legend()),
            )
            .properties(width="container", height=360)
        )
    )

    bottom_half_probability: float = sum(
        position_distributions[deck_size - 1][deck_size // 2 :]
    )
    middle_half_probability: float = sum(
        position_distributions[deck_size // 2][deck_size // 2 :]
    )

    mo.vstack(
        [
            distribution_chart,
            mo.md(
                f"""Probability of the bottom card ending up in the bottom half of the deck: {bottom_half_probability:2.1%}

    Probability of the middle card ending up in the bottom half of the deck: {middle_half_probability:2.1%}
    """
            )
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo, textwrap):
    mo.md(textwrap.dedent(r"""
    ## Entropy of the shuffle

    Now each histogram of final card positions may be treated as a probability distribution. If a card in a particular position in the original deck is shuffled uniformly at random into every possible deck position by the shuffle, its probability distribution will be uniform and so it will have maximal entropy. If it's consistently shuffled into the same position, it will have minimum entropy.

    The entropy, $S$, when calculated using logarithm base 2, is measured in bits of information,

    $$S = \sum_i -p_i \log_2(p_i)$$

    and so the entropy may be interpreted as the number of bits required to determine the card's final position in the deck after shuffling.
    """))
    return


@app.cell
def _(deck_size: int, log, position_distributions: "NDArray[np.float64]"):
    entropy_by_position: list[float] = [0 for _ in range(deck_size)]
    max_entropy: float = log(deck_size, 2)
    for _i in range(deck_size):
        entropy_by_position[_i] = sum(
            [
                (0 if probability == 0 else -probability * log(probability, 2))
                for probability in position_distributions[_i]
            ]
        )

    print("Maximum entropy = {:1.2} bits".format(max_entropy))
    return entropy_by_position, max_entropy


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The entropy of the final position distribution for each of the initial card positions is shown below. The cards near the middle of the deck all have nearly the maximum entropy of 5.7 bits and so these cards are being shuffled well. Cards near the top and bottom begin to fall off down to a low of 5.3.
    """)
    return


@app.cell
def _(
    alt,
    chart_config,
    chart_line_width: float,
    entropy_by_position: list[float],
):
    _rows: list[dict[str, float | int]] = [
        {"position": _position, "entropy": _entropy}
        for _position, _entropy in enumerate(entropy_by_position)
    ]

    chart_config(
        alt.Chart(alt.Data(values=_rows))
        .mark_line(strokeWidth=chart_line_width)
        .encode(
            x=alt.X("position:Q", title="Initial card position"),
            y=alt.Y("entropy:Q", title="Entropy of shuffled position/bits"),
        )
        .properties(width="container", height=360)
    )
    return


@app.cell(hide_code=True)
def _(mo, textwrap):
    mo.md(textwrap.dedent(r"""
    ## Trying some different shuffles

    After defining functions to do the shuffle testing and entropy calculation, any type of shuffle can be tested and their fairness can be compared using this entropy approach.
    """))
    return


@app.cell
def _(Callable, NDArray, floor, log, np):
    def repeat_shuffle(
        shuffle_function: Callable[[NDArray[np.integer]], NDArray[np.integer]],
        num_shuffles: int = 10000,
        deck_size: int = 52,
    ) -> NDArray[np.float64]:
        deck_size = int(deck_size)
        deck: NDArray[np.integer] = np.arange(deck_size)

        num_shuffles = int(num_shuffles)
        shuffle_weight: float = 1 / num_shuffles

        position_distributions: NDArray[np.float64] = np.zeros([deck_size, deck_size])

        for shuffle_index in range(num_shuffles):
            if shuffle_index % floor(num_shuffles / 2) == 0:
                print("Shuffling decks... {:.2%}".format(shuffle_index / num_shuffles))
            shuffled: NDArray[np.integer] = shuffle_function(deck)
            for position in range(deck_size):
                position_distributions[shuffled[position]][position] += shuffle_weight

        return position_distributions

    def entropy(distribution: NDArray[np.float64]) -> list[float]:
        deck_size: int = len(distribution)
        entropy_by_position: list[float] = [0 for _ in range(deck_size)]
        for position in range(deck_size):
            entropy_by_position[position] = sum(
                [
                    (0 if probability == 0 else -probability * log(probability, 2))
                    for probability in distribution[position]
                ]
            )
        return entropy_by_position

    return entropy, repeat_shuffle


@app.cell
def _(Callable, NDArray, box, cut, entropy, log, np, repeat_shuffle, riffle):
    shuffles: list[Callable[[NDArray[np.integer]], NDArray[np.integer]]] = [
        lambda deck: riffle(riffle(box(riffle(cut(deck))))),
        lambda deck: cut(riffle(box(riffle(riffle(deck))))),
        lambda deck: cut(riffle(riffle(riffle(box(deck))))),
    ]

    # Simulate many shuffles and calculate the entropy of each one
    distributions: list[NDArray[np.float64]] = [
        repeat_shuffle(shuffle_function) for shuffle_function in shuffles
    ]
    entropies: list[list[float]] = [
        entropy(distribution) for distribution in distributions
    ]
    max_entropies: list[float] = [
        log(len(distribution), 2) for distribution in distributions
    ]
    return distributions, entropies, max_entropies


@app.cell
def _(
    alt,
    chart_config,
    chart_line_width: float,
    distributions: "list[NDArray[np.float64]]",
    entropies: list[list[float]],
    inset_legend,
    max_entropies: list[float],
    max_entropy: float,
    mo,
):
    _entropy_rows: list[dict[str, float | int | str]] = []
    for shuffle_index, shuffle_entropy in enumerate(entropies):
        for _position, _entropy in enumerate(shuffle_entropy):
            _entropy_rows.append(
                {
                    "shuffle": "Shuffle {:1}".format(shuffle_index),
                    "position": _position,
                    "entropy": _entropy,
                }
            )

    _entropy_chart = (
        alt.Chart(alt.Data(values=_entropy_rows))
        .mark_line(strokeWidth=chart_line_width)
        .encode(
            x=alt.X("position:Q", title="Card position"),
            y=alt.Y("entropy:Q", title="Entropy/bits"),
            color=alt.Color("shuffle:N", title=None, legend=inset_legend()),
        )
        .properties(width="container", height=360)
    )

    if not all(max_entropies[0] == item for item in max_entropies):
        print("Invalid comparison - different max entropies")

    _max_entropy_line = (
        alt.Chart(alt.Data(values=[{"entropy": max_entropy, "label": "Max"}]))
        .mark_rule(strokeDash=[5, 5], color="#555", strokeWidth=chart_line_width)
        .encode(y="entropy:Q")
    )

    example_start_positions: list[int] = [0, 5, 20, 51]

    _example_charts: list[alt.Chart | alt.LayerChart] = []
    for start_position in example_start_positions:
        _example_rows: list[dict[str, float | int | str]] = []
        for shuffle_index, distribution in enumerate(distributions):
            for _position, _probability in enumerate(distribution[start_position]):
                _example_rows.append(
                    {
                        "shuffle": "Shuffle {:1}".format(shuffle_index),
                        "position": _position,
                        "probability": _probability,
                    }
                )

        _example_charts.append(
            chart_config(
                alt.Chart(
                    alt.Data(values=_example_rows),
                    title="Card starting in position {:}".format(start_position),
                )
                .mark_line(strokeWidth=chart_line_width)
                .encode(
                    x=alt.X("position:Q", title="Card position"),
                    y=alt.Y("probability:Q", title="Probability"),
                    color=alt.Color("shuffle:N", title=None, legend=inset_legend()),
                )
                .properties(width="container", height=264)
            )
        )

    mo.vstack(
        [
            chart_config(_entropy_chart + _max_entropy_line),
            mo.vstack(_example_charts, align="stretch"),
        ],
        align="stretch",
    )
    return


if __name__ == "__main__":
    app.run()
