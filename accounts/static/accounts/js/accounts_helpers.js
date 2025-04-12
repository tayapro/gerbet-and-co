function displayCountryName(countryCode) {
    let countryName = countryCode
    if (countryCode && countryCode.length === 2) {
        try {
            const displayNames = new Intl.DisplayNames(['en'], {
                type: 'region',
            })
            countryName = displayNames.of(countryCode.toUpperCase())
        } catch (error) {
            console.warn('Could not convert country code:', countryCode)
        }
    }
    return countryName
}
