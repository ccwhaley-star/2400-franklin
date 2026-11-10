// Copies each "inquiry" form submission into Cubby as a lead (the same call
// Cubby's own contact form makes), so prospects land in Cubby next to tenants.
//
// Netlify runs a function named `submission-created` after every form
// submission that passes its spam filter. The visitor never waits on this:
// the form, the thank-you message and the email notification work the same
// whether or not Cubby answers. Failures are logged (Netlify > Logs >
// Functions) and otherwise ignored.
//
// Env (Netlify site settings): CUBBY_STOREFRONT_KEY = the 2400 Franklin
// storefront key. FACILITY is Cubby's id for the 2400 Franklin facility
// (GET https://api.cubbystorage.com/sf/facilities/2400-franklin -> pricingGroups[].facilityExtId).

const FACILITY = "fac_UGvL8JM95Z8";
const ENDPOINT = "https://api.cubbystorage.com/sf/interests";

// "(785) 555-0100" / "785-555-0100" / "+1 785 555 0100" -> "+17855550100"; anything else -> undefined
function usPhone(raw) {
  const d = String(raw || "").replace(/\D/g, "");
  if (d.length === 10) return "+1" + d;
  if (d.length === 11 && d.startsWith("1")) return "+" + d;
  return undefined;
}

exports.handler = async (event) => {
  let payload;
  try {
    payload = JSON.parse(event.body).payload;
  } catch {
    return { statusCode: 400, body: "bad payload" };
  }
  if (!payload || payload.form_name !== "inquiry") return { statusCode: 200, body: "not an inquiry" };

  const key = process.env.CUBBY_STOREFRONT_KEY;
  if (!key) {
    console.log("CUBBY_STOREFRONT_KEY not set; inquiry not copied to Cubby");
    return { statusCode: 200, body: "no key" };
  }

  const f = payload.data || {};
  const clean = (v) => String(v || "").trim();
  const email = clean(f.email);
  const phone = usPhone(f.phone);
  const message = [
    clean(f.space) && `Space needed: ${clean(f.space)}`,
    clean(f.business) && `Business: ${clean(f.business)}`,
    clean(f.use) && `Use: ${clean(f.use)}`,
    !phone && clean(f.phone) && `Phone as typed: ${clean(f.phone)}`,
    "Sent from the 2400franklin.com inquiry form.",
  ].filter(Boolean).join("\n");

  const body = {
    facilityExtId: FACILITY,
    contact: {
      name: clean(f.name) || clean(f.business) || "Website inquiry",
      address: { ...(email && { email }), ...(phone && { phone }) },
    },
    message,
    source: "CONTACT_FORM",
  };

  try {
    const res = await fetch(ENDPOINT, {
      method: "POST",
      headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const text = await res.text();
    if (!res.ok) console.log(`Cubby rejected the inquiry (${res.status}): ${text.slice(0, 300)}`);
    else console.log(`Inquiry copied to Cubby: ${text.slice(0, 120)}`);
  } catch (e) {
    console.log(`Could not reach Cubby: ${e && e.message}`);
  }
  return { statusCode: 200, body: "ok" };
};
