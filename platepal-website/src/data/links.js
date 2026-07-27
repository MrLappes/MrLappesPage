/**
 * Linktree data — edit this file to add / remove / update links.
 *
 * Each entry supports:
 *   id          – unique number
 *   title       – displayed as the card heading
 *   description – short subtitle text
 *   url         – the link destination
 *   image       – URL or local path (relative to /public) for the thumbnail
 *   iconSvg     – (optional) raw SVG path string; renders instead of image if set
 *                  provide a viewBox string alongside it (default "0 0 24 24")
 *   category    – translation key used for filtering (must match linktree.categories.* in locales)
 */

export const links = [
  {
    id: 1,
    title: 'PlatePal Tracker',
    description: 'Open-source calorie tracker — currently in internal beta on Google Play.',
    url: 'https://github.com/MrLappes/platepal-tracker-flutter',
    image: '/icon.png',
    category: 'dev',
  },
  {
    id: 2,
    title: 'KingShakerz Custom Shaker Case',
    description: '3D-printable custom shaker case model on Printables.',
    url: 'https://www.printables.com/model/1611877-king-shakerz-custom-shaker-case',
    iconSvg: 'm0 35 12.172-7L0 21ZM12.172 0 0 7l12.172 7v14l12.172-7V7Z',
    iconViewBox: '0 0 24.344 42',
    category: '3d',
  },
  {
    id: 3,
    title: 'Instagram',
    description: '@mrlappes',
    url: 'https://www.instagram.com/mrlappes/',
    image: '/instagram.png',
    category: 'social',
  },
  {
    id: 4,
    title: 'Itch.io',
    description: 'My indie games.',
    url: 'https://mrlappes.itch.io/',
    image: '/itch-io.png',
    category: 'games',
  },
];

/** Unique category keys derived from the data — used to build filter chips. */
export const categories = [...new Set(links.map((l) => l.category))];
