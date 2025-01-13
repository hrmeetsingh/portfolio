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
    title: 'Harmeet Singh Salech - Quality Assurance',
    description: 'Harmeet Singh Salech | SDET | Quality Assurance | Quality Consulting | Software Automation | Deployments | DevOps',
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
    medium: 'hrmeet',
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
      '', // Empty fileUrl will hide the `Download Resume` button.
  },
  skills: [
    'PlayWright',
    'Cypress',
    'Selenium',
    'Appium',
    'WDIO',
    'JavaScript',
    'Java',
    'Node.js',
    'Scala',
    'SQL',
    'MongoDB',
    'Apache Spark',
    'Apache Kafka',
    'JMeter',
    'K6',
    'Gatling',
    'TypeScript',
    'Git',
    'Jira',
    'Docker',
    'Python',
    'CI/CD',
    'Test Strategy',
    'Test Planning',
    'C',
    'C++',
    'Microsoft Azure',
    'AWS',
    'Analytics',
  ],
  experiences: [
    {
      company: 'Royal Bank of Canada, Calgary',
      position: 'Senior SDET',
      from: 'Oct 2024',
      to: 'Present',
      companyLink: 'https://www.rbcroyalbank.com/',
    },
    {
      company: 'Neo Financial, Calgary',
      position: 'Senior Analyst',
      from: 'Oct 2023',
      to: 'Aug 2024',
      companyLink: 'https://www.neofinancial.com',
    },
    {
      company: 'ThoughtWorks, India',
      position: 'Lead Consultant',
      from: 'Dec 2015',
      to: 'Aug 2023',
      companyLink: 'https://www.thoughtworks.com',
    },
    {
      company: 'Pitney Bowes, India',
      position: 'Advisory QA Engineer',
      from: 'Jan 2012',
      to: 'Dec 2015',
      companyLink: 'https://www.pitneybowes.com',
    },
    {
      company: 'Adobe Inc, India',
      position: 'Senior Software Engineer',
      from: 'Aug 2010',
      to: 'Jan 2012',
      companyLink: 'https://www.adobe.com',
    },
    {
      company: 'TechMahindra Ltd, India',
      position: 'Software Engineer',
      from: 'Jun 2007',
      to: 'May 2010',
      companyLink: 'https://www.techmahindra.com',
    },
  ],
  certifications: [
    {
      name: 'Project Management Professional',
      body: 'Project Management Institute',
      year: 'Nov 2014',
      number: '1766389',
      link: 'https://www.pmi.org/',
    },
    {
      name: 'Certified Scrum Master',
      body: 'Scrum Alliance',
      year: 'May 2014',
      number: '000325939',
      link: 'https://www.scrumalliance.org/',
    },
  ],
  educations: [
    {
      institution: 'Punjab Technical University, Jalandhar, India',
      degree: 'Bachelor of Technology',
      specialization: 'Electronics & Communication Engineering',
      from: '2003',
      to: '2007',
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
    source: 'medium', 
    username: 'hrmeet', 
    limit: 5, 
  },
  googleAnalytics: {
    id: 'G-W5PQFBP1JF', // GA3 tracking id/GA4 tag id UA-XXXXXXXXX-X | G-XXXXXXXXXX
  },
  // Track visitor interaction and behavior. https://www.hotjar.com
  hotjar: {
    id: '',
    snippetVersion: 6,
  },
  themeConfig: {
    defaultTheme: 'black',

    // Hides the switch in the navbar
    // Useful if you want to support a single color mode
    disableSwitch: true,

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

  enablePWA: true,
};

export default CONFIG;
