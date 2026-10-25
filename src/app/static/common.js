// Shared by all pages.

// The backend only knows symbol codes (decision 0009); the display is decided
// here. Blanks are shown explicitly.
const EMOJI = {
    CHERRY: "🍒",
    LEMON: "🍋",
    BELL: "🔔",
    BAR: "💰",
    SEVEN: "7️⃣",
    BLANK: "⬜",
};

// All symbol codes, in the order used by the configuration editor.
const SYMBOLS = Object.keys(EMOJI);