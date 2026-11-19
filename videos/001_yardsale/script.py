"""Narration for video 001. Every number comes from results.json (experiments.py).
SCENES: list of (scene_id, [(line_id, text), ...]). One audio file per line."""

TITLE = "I Gave 1,000 People the Same Money. One Ended Up With Almost All of It."

SCENES = [
 ("hook", [
  ("h1", "This is a thousand people. Every one of them starts with exactly one hundred dollars. They're going to trade with each other, over and over. Every trade is a fair coin flip. Nobody is smarter. Nobody cheats. Nobody even has a plan."),
  ("h2", "Let's press play."),
  ("h3", "That is one person, holding eighty-three percent of all the money in this world. Half the population, put together, owns less than a single cent. Nobody cheated. Every trade was fair. So what happened?"),
 ]),
 ("rules", [
  ("r1", "Here are the rules. Two people meet at random. They look at whoever has less money, and each of them puts twenty percent of that amount on the table. Then they flip a coin. Winner takes the pot."),
  ("r2", "So if one has a hundred dollars and the other has fifty, they each put in ten. It doesn't matter who's richer. The coin treats them exactly the same."),
  ("r3", "Physicists and economists have been studying this for about twenty years. It's called the yard sale model. And on paper, it's the fairest economy you could design. No one has an edge. Money is never created or destroyed. It only moves."),
 ]),
 ("run", [
  ("u1", "So let's run it again, slowly this time, and keep score. After ten rounds, not much has changed. Some people are up a little, some are down a little."),
  ("u2", "After a hundred rounds, things are stretching. The person right in the middle of the pack is down to thirty-four dollars. And the richest one percent, just ten people, hold seven percent of everything."),
  ("u3", "After a thousand rounds, those ten people hold thirty-one percent. The bottom half of the population, five hundred people, are sharing seventeen cents."),
  ("u4", "By round ten thousand, ten people own ninety-four percent of the money. And it doesn't stop there. Keep going, and it ends with one."),
  ("u5", "Remember, every single one of those trades was a fair coin flip. So where is the unfairness hiding?"),
 ]),
 ("why", [
  ("w1", "It's hiding in a piece of arithmetic that feels wrong. Take a hundred dollars. Win twenty percent, and you have a hundred and twenty. Now lose twenty percent. You are not back at a hundred. You're at ninety-six. A win and a loss don't cancel out. The loss is a slice of a bigger pile than the win was."),
  ("w2", "Now here's the catch. The stake is always twenty percent of the poorer person's money. So for the poorer person, every flip is a huge swing: plus or minus a fifth of everything they have. For the richer person, the very same bet is pocket change."),
  ("w3", "Give the rich one ten losses in a row, and they're down two percent. Give the poor one ten losses in a row, and almost ninety percent of what they had is gone."),
 ]),
 ("solo", [
  ("s1", "We can test what that does to a person. Take one player and give them a hundred fair bets in a row, each one plus or minus twenty percent. Then repeat that a million times."),
  ("s2", "The average result is a hundred dollars. Exactly fair, just like the coin promised. But that average is being held up by a handful of enormous winners. Eighty-six percent of players end up with less than they started with. The typical one finishes with thirteen dollars."),
  ("s3", "Just to break even, you would need to win fifty-six flips out of a hundred. A fair coin rarely hands you that."),
  ("s4", "That's the trap. The game is fair on average, and bad for almost everybody who plays it. And in every trade, the poorer partner is the one playing this version of the game. So money drifts, slowly, with nobody intending it, uphill."),
 ]),
 ("worlds", [
  ("m1", "But maybe the person who ends up with everything earned it somehow. Maybe they started in the right spot. So we built ten thousand separate worlds. A hundred people in each. Same rules, different coin flips."),
  ("m2", "In every single world, somebody ended up on top, holding on average more than half of all the money. But it was never the same somebody. Each of the hundred seats won about one percent of the time. Who wins is pure luck."),
  ("m3", "What isn't luck is that there is a winner. And early luck sticks. After just ten rounds, the eventual winner was already ahead in two worlds out of three. After two hundred rounds, they were almost always in the top half, and usually in the top ten. A few lucky flips at the start, and the arithmetic does the rest."),
 ]),
 ("talent", [
  ("k1", "One more question. What if some people really are better? Let's give a hundred of our thousand a real edge: against anyone else, they win fifty-five percent of the time."),
  ("k2", "We ran that world two hundred times. The edge matters. In ninety-eight percent of runs, the richest person was one of the skilled, and together the skilled ended up holding nearly all of the money."),
  ("k3", "But look closer. Eighty percent of the skilled players still finished with less than they started with. Nearly two thirds of them finished with under a dollar. Talent decides which group the winner comes from. It doesn't rescue most of the talented."),
 ]),
 ("tax", [
  ("t1", "So is that just how it has to end? Let's change one rule. Every round, everybody pays a tiny wealth tax, one tenth of one percent of what they have, and the pot is shared out equally."),
  ("t2", "Same people. Same coin flips. But now it never collapses into one. It settles. The top one percent hold about twenty percent of the wealth, and the bottom half about three. If that shape looks familiar, it should. In the United States, the top one percent hold about a third of the wealth, and the bottom half under three percent."),
  ("t3", "Turn the dial up to one percent a round, and the top one percent hold just five."),
  ("t4", "That's the uncomfortable thing this model says. Extreme inequality doesn't need greed, or talent, or cheating. It's what fair exchange does when it's left alone. Staying even takes something pushing the other way."),
 ]),
 ("outro", [
  ("o1", "Now, this is a toy. Real people work, save, invent things and create new wealth, and real trades aren't coin flips. The model leaves all of that out on purpose. Its point is narrow: take away every unfair advantage, and the gap still opens."),
  ("o2", "What a society should do about that is a real argument, and a simulation can't settle it. But it can tell us what happens by default."),
  ("o3", "All the code for this video is linked below. Change the rules. Run your own world. And next time: if luck matters this much for money, how much does it matter for success? We're going to simulate ten thousand careers and find out."),
 ]),
]

if __name__ == "__main__":
    n = sum(len(t) for _, ls in SCENES for _, t in ls)
    words = sum(len(t.split()) for _, ls in SCENES for _, t in ls)
    print(f"{sum(len(ls) for _, ls in SCENES)} lines, {words} words, {n} chars")
