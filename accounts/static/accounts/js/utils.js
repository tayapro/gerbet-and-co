/**
 * Converts a two-letter country code into the full country name.
 *
 * - Uses the Intl.DisplayNames API for localization.
 * - Falls back to returning the original code if conversion fails.
 *
 * @param {string} countryCode - Two-letter ISO country code.
 * @returns {string} - Full country name or original code if unavailable.
 */
function displayCountryName(countryCode) {
    let countryName = countryCode;
    if (countryCode && countryCode.length === 2) {
        try {
            const displayNames = new Intl.DisplayNames(['en'], {
                type: 'region',
            });
            countryName = displayNames.of(countryCode.toUpperCase());
        } catch (error) {
            console.warn('Could not convert country code:', countryCode);
        }
    }
    return countryName;
}
