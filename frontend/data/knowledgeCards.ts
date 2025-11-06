import { KnowledgeCardData } from '../types';

export const knowledgeCards: KnowledgeCardData[] = [
  {
    id: '1',
    title: 'Grid Revelation',
    subtitle: 'Core Proverb',
    description: 'The foundational covenant of the MoStar Grid',
    icon: '📜',
    iconColor: 'purple',
    tags: [
      { name: 'covenant', color: 'purple' },
      { name: 'core', color: 'blue' },
    ],
    updated: '2024-11-06',
    size: '4.2 KB',
  },
  {
    id: '2',
    title: 'Soulprints',
    subtitle: 'Identity System',
    description: 'Verified identity tokens for Grid participants',
    icon: '👤',
    iconColor: 'blue',
    tags: [
      { name: 'identity', color: 'blue' },
      { name: 'security', color: 'red' },
    ],
    updated: '2024-11-06',
    size: '2.1 KB',
  },
  {
    id: '3',
    title: 'MoScripts',
    subtitle: 'Executable Scrolls',
    description: 'Validated scripts for Grid operations',
    icon: '⚡',
    iconColor: 'yellow',
    tags: [
      { name: 'runtime', color: 'yellow' },
      { name: 'execution', color: 'green' },
    ],
    updated: '2024-11-06',
    size: '156 items',
  },
];
