// gitprofile.config.ts

const CONFIG = {
  github: {
    username: 'hrmeetsingh',
  },
  /**
   * If you are deploying to https://<USERNAME>.github.io/, for example your repository is at https://github.com/arifszn/arifszn.github.io, set base to '/'.
   * If you are deploying to https://<USERNAME>.github.io/<REPO_NAME>/,
   * for example your repository is at https://github.com/arifszn/portfolio, then set base to '/portfolio/'.
   */
  base: '/portfolio/',
  projects: {
    github: {
      display: true,
      header: 'Github Projects',
      mode: 'manual',
      automatic: {
        sortBy: 'stars', 
        limit: 6,
        exclude: {
          forks: true, 
          projects: [], // These projects will not be displayed. example: ['arifszn/my-project1', 'arifszn/my-project2']
        },
      },
      manual: {
        projects: ['hrmeetsingh/playwright-layout-testing', 'hrmeetsingh/turborepo-ui-tests','hrmeetsingh/ChromeRemoteDebugREPL','hrmeetsingh/cypress-github-custom-actions','hrmeetsingh/EthereumPrivateChain','hrmeetsingh/OpenCV_Python'],
      },
    },
    external: {
      header: 'My Projects',
      projects: [
        // {
        //   title: 'Project Name',
        //   description:
        //     'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed euismod, nunc ut.',
        //   imageUrl:
        //     'https://img.freepik.com/free-vector/illustration-gallery-icon_53876-27002.jpg',
        //   link: 'https://example.com',
        // },
        // {
        //   title: 'Project Name',
        //   description:
        //     'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed euismod, nunc ut.',
        //   imageUrl:
        //     'https://img.freepik.com/free-vector/illustration-gallery-icon_53876-27002.jpg',
        //   link: 'https://example.com',
        // },
      ],
    },
  },
  seo: {
    title: 'Portfolio of Harmeet Singh',
    description: 'Portfolio of Harmeet Singh Salech',
    imageURL: 'https://avatars.githubusercontent.com/u/15318255?s…00&u=e5c4402f9822cd6e44cdc261ab05f06d9d1697c3&v=4',
  },
  social: {
    linkedin: 'hrmeetsingh',
    twitter: 'ErHarmeet',
    mastodon: 'HarmeetSalech@mastodon.social',
    researchGate: '',
    facebook: '',
    instagram: '',
    reddit: '',
    threads: '',
    youtube: '',
    udemy: '',
    dribbble: '',
    behance: '',
    medium: '',
    dev: '',
    stackoverflow: '', // example: '1/jeff-atwood'
    skype: '',
    telegram: '',
    website: '',
    phone: '',
    email: 'harmeetsalech@gmail.com',
  },
  resume: {
    fileUrl:
      'https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf', // Empty fileUrl will hide the `Download Resume` button.
  },
  skills: [
    'PHP',
    'Laravel',
    'JavaScript',
    'React.js',
    'Node.js',
    'Nest.js',
    'MySQL',
    'PostgreSQL',
    'Git',
    'Docker',
    'PHPUnit',
    'CSS',
    'Antd',
    'Tailwind',
  ],
  experiences: [
    {
      company: 'Company Name',
      position: 'Position',
      from: 'September 2021',
      to: 'Present',
      companyLink: 'https://example.com',
    },
    {
      company: 'Company Name',
      position: 'Position',
      from: 'July 2019',
      to: 'August 2021',
      companyLink: 'https://example.com',
    },
  ],
  certifications: [
    {
      name: 'Lorem ipsum',
      body: 'Lorem ipsum dolor sit amet',
      year: 'March 2022',
      link: 'https://example.com',
    },
  ],
  educations: [
    {
      institution: 'Institution Name',
      degree: 'Degree',
      from: '2015',
      to: '2019',
    },
    {
      institution: 'Institution Name',
      degree: 'Degree',
      from: '2012',
      to: '2014',
    },
  ],
  publications: [
    {
      title: 'Infrastructure as Code',
      conferenceName: 'GeekNight by ThoughtWorks NCR',
      journalName: '',
      authors: 'Harmeet Singh, Surjit Singh',
      link: 'https://www.slideshare.net/HarmeetSingh131/infrastrucutre-as-code-88707639',
      description:
        'Applying principles and practices towards IaC automation and perform automated testing for the same. Presented at ThoughtWorks Gurgaon GeekNight Feb 2018',
    },
    {
      title: 'Web Security 101 - Workshop',
      conferenceName: 'XConf 2018',
      journalName: '',
      authors: 'Harmeet Singh',
      link: 'https://hrmeetsingh.github.io/WebSec-101/',
      description:
        'Hands on workshop on basics of web security from NCR XConf 2018, New Delhi. Covers topic ranging from Application Security, Networking Basics, Cryptography, Proxies to common attack vectors',
    },
    {
      title: 'Web Automation using Taiko',
      conferenceName: 'VodQA NCR 2019',
      journalName: '',
      authors: 'Harmeet Singh, Divya Rakhiani',
      link: 'https://www.youtube.com/watch?v=VzdvHN2UTNg',
      description:
        'VodQA 2019 Gurgaon talk on Taiko - ChromeDevTools protocol based web automation tool by ThoughtWorks',
    },
    {
      title: 'Handling PDF Review Comments in FrameMaker',
      conferenceName: '',
      journalName: 'Adobe Blogs',
      authors: 'Harmeet Singh',
      link: 'https://blog.adobe.com/en/publish/2011/05/02/handling-pdf-review-comments-in-framemaker',
      description:
        'Adobe engineering blog demonstrating a powerful feature of Adobe FrameMaker - importing PDF comments from reviewed PDFs to iteratively incorporate feedback into the technical authoring process',
    },
  ],
  // Display articles from your medium or dev account. (Optional)
  blog: {
    source: 'dev', // medium | dev
    username: 'arifszn', // to hide blog section, keep it empty
    limit: 2, // How many articles to display. Max is 10.
  },
  googleAnalytics: {
    id: '', // GA3 tracking id/GA4 tag id UA-XXXXXXXXX-X | G-XXXXXXXXXX
  },
  // Track visitor interaction and behavior. https://www.hotjar.com
  hotjar: {
    id: '',
    snippetVersion: 6,
  },
  themeConfig: {
    defaultTheme: 'lofi',

    // Hides the switch in the navbar
    // Useful if you want to support a single color mode
    disableSwitch: false,

    // Should use the prefers-color-scheme media-query,
    // using user system preferences, instead of the hardcoded defaultTheme
    respectPrefersColorScheme: false,

    // Display the ring in Profile picture
    displayAvatarRing: true,

    // Available themes. To remove any theme, exclude from here.
    themes: [
      'light',
      'dark',
      'cupcake',
      'bumblebee',
      'emerald',
      'corporate',
      'synthwave',
      'retro',
      'cyberpunk',
      'valentine',
      'halloween',
      'garden',
      'forest',
      'aqua',
      'lofi',
      'pastel',
      'fantasy',
      'wireframe',
      'black',
      'luxury',
      'dracula',
      'cmyk',
      'autumn',
      'business',
      'acid',
      'lemonade',
      'night',
      'coffee',
      'winter',
      'dim',
      'nord',
      'sunset',
      'procyon',
    ],

    // Custom theme, applied to `procyon` theme
    customTheme: {
      primary: '#fc055b',
      secondary: '#219aaf',
      accent: '#e8d03a',
      neutral: '#2A2730',
      'base-100': '#E3E3ED',
      '--rounded-box': '3rem',
      '--rounded-btn': '3rem',
    },
  },

  // Optional Footer. Supports plain text or HTML.
  footer: `Made with <a 
      class="text-primary" href="https://github.com/arifszn/gitprofile"
      target="_blank"
      rel="noreferrer"
    >GitProfile</a> and ❤️`,

  enablePWA: true,
};

export default CONFIG;
