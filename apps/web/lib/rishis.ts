export const RISHI_ORDER = [
  "atri",
  "bharadvaja",
  "gautama",
  "jamadagni",
  "kashyapa",
  "vashistha",
  "vishvamitra",
] as const;

export type RishiId = (typeof RISHI_ORDER)[number];

export const RISHI_LABEL: Record<RishiId, string> = {
  atri: "Atri",
  bharadvaja: "Bharadvaja",
  gautama: "Gautama",
  jamadagni: "Jamadagni",
  kashyapa: "Kashyapa",
  vashistha: "Vashistha",
  vishvamitra: "Vishvamitra",
};

export const RISHI_DOMAIN: Record<RishiId, string> = {
  atri: "Weather",
  bharadvaja: "Grocery",
  gautama: "Banking",
  jamadagni: "Ecommerce",
  kashyapa: "Agriculture",
  vashistha: "Insurance",
  vishvamitra: "Stocks",
};
