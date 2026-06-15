// Single source of truth for the main navigation.
// Edit ONCE here, and every page rerenders with the new nav.
export type NavItem = {
  href: string;
  label: string;
  external?: boolean;
};

export const NAV_MAIN: NavItem[] = [
  { href: '/kilimanjaro', label: 'Climb Kilimanjaro' },
  { href: '/safari', label: 'Tanzania Safaris' },
  { href: '/daytrips', label: 'Day Trips' },
];

export const NAV_DROPDOWN_LABEL = 'Plan Your Trip';

export const NAV_DROPDOWN: NavItem[] = [
  { href: '/safety', label: 'Safety & Rescue' },
  { href: '/travel-guide', label: 'Travel Guide' },
  { href: '/packing-list', label: 'Packing List' },
  { href: '/training-plan', label: 'Training Plan' },
  { href: '/compare-routes', label: 'Compare Routes' },
  { href: '/choose-operator', label: 'Choose an Operator' },
  { href: '/glacier-tour', label: 'Glacier Tour' },
  { href: '/gallery', label: 'Photo Gallery' },
];

export const NAV_AFTER: NavItem[] = [
  { href: '/blog', label: 'Blog' },
  { href: '/about', label: 'About Us' },
  { href: '/contact', label: 'Contact' },
];

export const FOOTER_KILIMANJARO: NavItem[] = [
  { href: '/kilimanjaro', label: 'All Routes' },
  { href: '/compare-routes', label: 'Compare Routes' },
  { href: '/packing-list', label: 'Packing List' },
  { href: '/training-plan', label: 'Training Plan' },
  { href: '/glacier-tour', label: 'Glacier Tour' },
];

export const FOOTER_PLAN: NavItem[] = [
  { href: '/safety', label: 'Safety & Rescue' },
  { href: '/travel-guide', label: 'Travel Guide' },
  { href: '/choose-operator', label: 'Choose an Operator' },
  { href: '/blog', label: 'Blog' },
  { href: '/destinations', label: 'Destinations Guide' },
];

export const FOOTER_COMPANY: NavItem[] = [
  { href: '/', label: 'Home' },
  { href: '/about', label: 'About Us' },
  { href: '/stories', label: 'Climber Stories' },
  { href: '/gallery', label: 'Photo Gallery' },
  { href: '/faith-vision-foundation', label: 'Faith Vision Foundation' },
  { href: '/charity-climbs', label: 'Charity Climbs' },
  { href: '/corporate-climbs', label: 'Corporate Team Climbs' },
  { href: '/partners', label: 'Travel Agency Partners' },
  { href: '/contact', label: 'Contact' },
];
