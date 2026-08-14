// Single source of truth for sitewide constants.
export const SITE = {
  baseUrl: 'https://gokilimanjarotreks.com',
  name: 'Go Kilimanjaro Treks',
  description: 'Expert-guided Mount Kilimanjaro climbs and Tanzania safaris from Moshi.',
  shortDescription: 'Expert-guided Kilimanjaro climbs and Tanzania safaris from Moshi.',
  founder: 'Nelson Mushi',
  phone: '+255 677 917 500',
  phoneIntl: '+255677917500',
  emergencyPhone: '+255 713 917 500',
  emergencyPhoneIntl: '+255713917500',
  email: 'info@gokilimanjarotreks.com',
  whatsapp: 'https://wa.me/255677917500',
  // Google Apps Script web-app URL for logging leads to a Sheet. Leave '' to
  // disable; paste the deployed /exec URL here to switch lead logging on.
  sheetEndpoint: '',
  address: {
    street: 'NHC Building Block B, Apartment No. 106, Boma / Rhindi Line Road',
    locality: 'Moshi',
    region: 'Kilimanjaro',
    country: 'TZ',
    countryName: 'Tanzania',
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

/** The two offices, exactly as the company supplied them. */
export const OFFICES = [
  {
    id: 'moshi',
    label: 'Head Office',
    name: 'Gokilimanjarotreks Office',
    person: 'Nelson Mushi',
    role: 'Founder and lead guide',
    whatsapp: '+255 677 917 500',
    whatsappIntl: '255677917500',
    // The office line is already published sitewide as a callable number.
    voice: true,
    emergency: '+255 713 917 500',
    emergencyIntl: '+255713917500',
    email: 'info@gokilimanjarotreks.com',
    addressLines: [
      'NHC Building Block B, Apartment No. 106',
      'Boma / Rhindi Line Road',
      'Moshi, Kilimanjaro, Tanzania',
    ],
    streetAddress: 'NHC Building Block B, Apartment No. 106, Boma / Rhindi Line Road',
    locality: 'Moshi',
    region: 'Kilimanjaro',
    countryName: 'Tanzania',
    country: 'TZ',
  },
  {
    id: 'kenya',
    label: 'Kenya Office',
    name: 'Gokilimanjarotreks Kenya',
    person: 'Andrew Thande',
    role: 'Kenya representative',
    whatsapp: '+254 713 439 669',
    whatsappIntl: '254713439669',
    // Supplied as a WhatsApp contact only, so no tel: link is asserted.
    voice: false,
    emergency: null,
    emergencyIntl: null,
    email: 'thandegokilimanjarotreks@gmail.com',
    addressLines: ['Nairobi, Kenya'],
    streetAddress: null,
    locality: 'Nairobi',
    region: null,
    countryName: 'Kenya',
    country: 'KE',
  },
] as const;

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
    url: `${SITE.baseUrl}/about`,
  },
  telephone: SITE.phoneIntl,
  email: SITE.email,
  address: {
    '@type': 'PostalAddress',
    streetAddress: SITE.address.street,
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
    {
      '@type': 'ContactPoint',
      telephone: SITE.emergencyPhoneIntl,
      contactType: 'emergency',
      areaServed: 'TZ',
      availableLanguage: ['English', 'Swahili'],
    },
    {
      '@type': 'ContactPoint',
      telephone: '+254713439669',
      email: 'thandegokilimanjarotreks@gmail.com',
      contactType: 'customer service',
      areaServed: 'KE',
      availableLanguage: ['English', 'Swahili'],
    },
  ],
  subOrganization: [
    {
      '@type': 'TravelAgency',
      '@id': `${SITE.baseUrl}/contact#kenya-office`,
      name: 'Gokilimanjarotreks Kenya',
      telephone: '+254713439669',
      email: 'thandegokilimanjarotreks@gmail.com',
      employee: { '@type': 'Person', name: 'Andrew Thande' },
      address: {
        '@type': 'PostalAddress',
        addressLocality: 'Nairobi',
        addressCountry: 'KE',
      },
      parentOrganization: { '@id': `${SITE.baseUrl}/#organization` },
    },
  ],
  sameAs: [SITE.social.facebook, SITE.social.instagram],
};
