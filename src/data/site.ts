// Single source of truth for sitewide constants.
export const SITE = {
  baseUrl: 'https://gokilimanjarotreks.com',
  name: 'Go Kilimanjaro Treks',
  description: 'Expert-guided Mount Kilimanjaro climbs and Tanzania safaris from Moshi.',
  shortDescription: 'Expert-guided Kilimanjaro climbs and Tanzania safaris from Moshi.',
  founder: 'Nelson Mushi',
  phone: '+255 677 917 500',
  phoneIntl: '+255677917500',
  email: 'info@gokilimanjarotreks.com',
  whatsapp: 'https://wa.me/255677917500',
  address: {
    locality: 'Moshi',
    region: 'Kilimanjaro',
    country: 'TZ',
    lat: '-3.3731',
    lng: '37.3441',
  },
  social: {
    facebook: 'https://www.facebook.com/gokilimanjarotreks',
    instagram: 'https://www.instagram.com/gokilimanjarotreks',
  },
  // For the floating WhatsApp tooltip
  whatsappPrefill: {
    booking: 'Hi%20Nelson%2C%20I%27d%20like%20to%20plan%20a%20climb.',
    partnership: 'Hi%20Nelson%2C%20I%27d%20like%20to%20discuss%20a%20travel%20agency%20partnership.',
    charity: 'Hi%20Nelson%2C%20I%27d%20like%20to%20discuss%20a%20charity%20climb.',
    faith: 'Hi%20Nelson%2C%20I%27d%20like%20to%20talk%20about%20the%20Faith%20Vision%20Foundation.',
  },
} as const;

export const ORG_LD = {
  '@context': 'https://schema.org',
  '@type': 'TravelAgency',
  '@id': `${SITE.baseUrl}/#organization`,
  name: SITE.name,
  alternateName: 'Gokilimanjaro Treks',
  url: SITE.baseUrl,
  logo: {
    '@type': 'ImageObject',
    url: `${SITE.baseUrl}/images/logo.png`,
    width: 1600,
    height: 1132,
  },
  image: `${SITE.baseUrl}/images/og-home.jpg`,
  description: 'Expert-guided Mount Kilimanjaro climbs and Tanzania safaris with Nelson Mushi. Based in Moshi, Tanzania.',
  foundingDate: '2010',
  founder: {
    '@type': 'Person',
    name: SITE.founder,
    url: `${SITE.baseUrl}/about.html`,
  },
  address: {
    '@type': 'PostalAddress',
    addressLocality: SITE.address.locality,
    addressRegion: SITE.address.region,
    addressCountry: SITE.address.country,
  },
  geo: {
    '@type': 'GeoCoordinates',
    latitude: SITE.address.lat,
    longitude: SITE.address.lng,
  },
  contactPoint: [
    {
      '@type': 'ContactPoint',
      telephone: SITE.phoneIntl,
      email: SITE.email,
      contactType: 'customer service',
      areaServed: 'TZ',
      availableLanguage: ['English', 'Swahili'],
    },
  ],
  sameAs: [SITE.social.facebook, SITE.social.instagram],
};
