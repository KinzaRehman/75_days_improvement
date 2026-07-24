/**
 * quotes.js
 * ------------------------------------------------------------------
 * One original motivational line per challenge day (75 total), written
 * for this project specifically to avoid reproducing anyone else's
 * copyrighted quote collection inside a paid product.
 */

'use strict';

    const QUOTES = [
      "Discipline is choosing between what you want now and what you want most.",
      "Small daily choices are the compound interest of self-respect.",
      "You don't have to be extreme, just consistent.",
      "The body achieves what the mind believes.",
      "Progress is quiet before it's visible.",
      "Show up for yourself the way you'd show up for someone you love.",
      "Every rep, every page, every glass of water is a vote for who you're becoming.",
      "Motivation gets you started. Habit keeps you going.",
      "Today's effort is tomorrow's evidence.",
      "You are not starting over, you are starting stronger.",
      "Comfort and growth rarely live in the same room.",
      "Consistency is the quiet superpower.",
      "Your future self is watching, and thanking you.",
      "Hard days build the muscle that easy days can't.",
      "One honest day beats seven perfect intentions.",
      "Energy follows action, not the other way around.",
      "Discipline is a form of self-love.",
      "Keep the promise you made to yourself.",
      "Slow progress is still progress.",
      "You're not chasing perfect, you're chasing consistent.",
      "The days you don't want to show up matter the most.",
      "Strength is built one uncomfortable choice at a time.",
      "Trust the process, not just the mood.",
      "Nobody regrets the workout they finished.",
      "Rest is part of the plan, not a break from it.",
      "Your habits are voting for the person you'll become.",
      "Do it for the version of you that gave up before.",
      "A little progress each day adds up to big results.",
      "The hardest part is starting. You've already done that.",
      "You're allowed to go slow, just don't stop.",
      "Every day is a fresh page, not a fresh judgment.",
      "Growth is uncomfortable by design.",
      "What you repeat, you become.",
      "Show up. That's most of the battle.",
      "You are capable of more than your excuses admit.",
      "This is the version of hard that gets easier.",
      "Small wins stack into big change.",
      "Keep going. The turnaround always comes after the hardest part.",
      "Your only competition is who you were yesterday.",
      "Effort compounds quietly, then all at once.",
      "Choose discomfort now so you can choose freedom later.",
      "Discipline looks boring until it looks like results.",
      "The work you do when no one's watching counts the most.",
      "You don't need more time, you need more decision.",
      "Every glass of water, every page, every step is progress you can feel.",
      "Consistency doesn't need to be loud to be powerful.",
      "You're allowed to be proud of small steps.",
      "Momentum is built one done task at a time.",
      "Today is a rep in the life you're building.",
      "Be stubborn about your goals, flexible about your methods.",
      "The version of you on day 75 is proud of day 1.",
      "Take care of your body, it's carrying your whole future.",
      "Habits are easier to keep than to start.",
      "You're not behind, you're building.",
      "A good day starts with a decision, not a mood.",
      "Progress hides in the days that feel unremarkable.",
      "What feels hard today is training for tomorrow.",
      "You get to choose who shows up today.",
      "Discipline is remembering what you want.",
      "Every checked box is a promise kept.",
      "You're building proof, not just progress.",
      "The best time to keep going was yesterday. The next best time is now.",
      "Some days you fight for motivation, other days it fights for you.",
      "Keep your standards higher than your excuses.",
      "You are the sum of what you repeat.",
      "Real change happens in ordinary moments, not big ones.",
      "Trust the boring, consistent work.",
      "You're not just tracking days, you're tracking becoming.",
      "The comeback is always stronger than the setback.",
      "Give today the effort you want tomorrow to remember.",
      "Strong habits are built in soft, quiet repetition.",
      "You don't need to feel ready, you just need to begin.",
      "Every day you choose yourself is a day well spent.",
      "The finish line looks a lot like day one, just braver.",
      "You made it to day 75. Look at what consistency built."
    ];

/**
 * Returns the quote for a given 1-based challenge day, wrapping around
 * if the day number ever exceeded the list length.
 */
function getQuoteForDay(day) {
  return QUOTES[(day - 1) % QUOTES.length];
}

module.exports = { QUOTES, getQuoteForDay };
