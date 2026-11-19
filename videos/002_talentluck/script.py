"""Narration for video 002 (Talent vs Luck). Written AFTER experiments.py; every number comes from results.json.
SCENES: list of (scene_id, [(line_id, text), ...]). One audio file per line.
Shape (different from 001): verdict first -> the rules -> rewind 10,000 lives -> the exchange rate ->
track records (the unplanned finding: luck has an address) -> who should get support -> limits -> close."""

SCENES = [
 ("cold", [
  ("c1", "Is success mostly talent, or mostly luck? Here are a thousand people. The brighter the colour, the more talented the person. Each of them starts a forty-year career with the same ten points of success. The gold dots drifting around are lucky breaks. The red ones are setbacks. Let's run all forty years."),
  ("c2", "This is the most successful person in this world. They finished with ten thousand, two hundred and forty points, about a thousand times what they started with. Their talent? Eight hundred and twelve people were more talented."),
  ("c3", "And this is the most talented person of all. In forty years, not one lucky break reached them. Not one setback, either. Their talent score was point nine one, the highest in the world. They ended exactly where they began."),
 ]),
 ("rules", [
  ("r1", "The rules come from a 2018 paper by three Italian researchers, Pluchino, Biondo and Rapisarda, called Talent versus Luck. Talent follows a bell curve. Most people are near average, a few are exceptional. Nobody's talent changes, and nobody moves."),
  ("r2", "Every six months, the dots drift. When a lucky break lands on you, you get a chance to double your success, and that chance is your talent. Someone with a talent of point nine grabs it nine times out of ten. Someone at point five, half the time. A setback halves you, no matter who you are."),
  ("r3", "In our last video, we played a game of pure coin flips, and even the players with a real edge mostly ended up poor. This world is different. It is built to reward talent. And still, after forty years, the top twenty percent hold eighty-three percent of all the success, while our most talented person stood still."),
 ]),
 ("rewind", [
  ("w1", "But that is one history. Maybe our genius was just unlucky. So we did something you can't do with real people. We kept the same thousand people, the same talents, the same seats, and replayed their forty years ten thousand times, each time with different breaks."),
  ("w2", "This is how often each person finished first, sorted from least talented to most. Talent clearly helps. The most talented tenth of the population produced a quarter of all the winners. The least talented tenth, about two percent."),
  ("w3", "Now find the most talented person. Out of ten thousand lives, they finished first forty-seven times. That's about five times more often than a random person, and it still means they lose ninety-nine and a half percent of the time. They made the top ten in only three percent of their lives, and finished below where they started in thirty-nine percent."),
  ("w4", "Nine hundred and seventy-six different people won at least once. The typical winner was more talented than about seven in ten people. Good, not exceptional. One winner in four had below-average talent."),
  ("w5", "What the winners did have was luck. On average, a winner met ten and a half lucky breaks in forty years. A typical person meets one and a half. And three winners out of four never had a single setback."),
 ]),
 ("exchange", [
  ("x1", "So how much is talent actually worth? Take every person, in every history, and ask what predicts where they ended up."),
  ("x2", "Talent, on its own, explains less than half a percent of the differences in success. Simply counting the good and bad breaks someone met explains ninety-two percent. If you wanted to guess how someone's career went, knowing their talent would barely help. Knowing their breaks would almost give you the answer."),
  ("x3", "Here is the exchange rate. One extra lucky break is worth, on average, as much as being almost four standard deviations more talented. That's the gap between an average person and the most gifted person in about twenty-three thousand. One extra setback costs more than six."),
  ("x4", "That doesn't make talent useless. Across all ten thousand lives, the people who won most often were ranked second, first and sixth in talent. Talent shows up across many lives. In any single life, it is buried under the breaks."),
 ]),
 ("record", [
  ("k1", "That has a practical sting. In real life we never see talent directly. We see track records. So let's do what a recruiter or an investor would do: stop the clock at year twenty, and pick the person with the best record. Their record looks spectacular: on average, they have doubled their success about six times."),
  ("k2", "How talented is that person? On average, more talented than two thirds of the population. They were the most talented person in less than half a percent of histories."),
  ("k3", "But here's a result we didn't expect. Over the next twenty years, the leader kept doing well. Forty percent of them grew further, against twenty percent of everyone else, and twenty-seven percent for the most talented person. So the record does predict the future. Why, if it mostly measures luck?"),
  ("k4", "Because in this world, luck has an address. The dots drift slowly, so a neighbourhood full of good breaks stays good for years. Sitting in the same seat, the leader met about twice as many lucky breaks in their second twenty years as everyone else."),
  ("k5", "So we tested it. Same people, but for the second twenty years, everyone gets a fresh world. The leader's edge almost vanishes. Twenty-two percent of them grow, about the same as anybody. The most talented person still grows in twenty-seven percent. The record was real. It just wasn't about the person."),
 ]),
 ("support", [
  ("p1", "The paper's authors asked a policy question. If you have resources to support people, who should get them? We tested it on our thousand. Every five years we hand out the same budget under four different rules, and count how many of the hundred and forty-nine most talented people end their careers ahead."),
  ("p2", "With no support at all, thirty-one percent of them end up ahead. Give the budget to the top ten percent by success, and it barely moves: thirty-four. The top quarter: forty-one. A random quarter: sixty-eight. Split equally between everyone: seventy-one."),
  ("p3", "Rewarding past success mostly rewards past luck. Spreading the same budget widely gives talent more chances to meet a lucky break. That is the same ranking the original paper found."),
 ]),
 ("limits", [
  ("l1", "Now, what this model can't tell you. Talent here is fixed, and luck is completely separate from it. Real people learn, choose where to stand, and try again, which is a way of collecting more breaks. And real success isn't a number that only doubles or halves."),
  ("l2", "The results also depend on settings nobody can measure. Make talent twice as unequal, and the typical winner gets better: more talented than seventy-nine percent of people, instead of sixty-nine. But talent still explains under two percent of the differences."),
  ("l3", "So this doesn't prove that success is luck, and it isn't career advice. It shows something narrower. Even in a world built to reward talent, a few random breaks can outweigh a lot of it, and a track record can't tell you which one you're looking at."),
 ]),
 ("outro", [
  ("o1", "Across ten thousand lives, talent shows. In any one life, it's mostly the breaks. If you want to see how luck alone turns into wealth when nobody has any talent at all, watch our previous video, Why the Rich Get Richer, Even in a Perfectly Fair Game. Everything we ran for both experiments is listed in the description."),
 ]),
]

if __name__ == "__main__":
    n = sum(len(t) for _, ls in SCENES for _, t in ls)
    words = sum(len(t.split()) for _, ls in SCENES for _, t in ls)
    print(f"{sum(len(ls) for _, ls in SCENES)} lines, {words} words, {n} chars, ~{words / 173:.1f} min of speech")
