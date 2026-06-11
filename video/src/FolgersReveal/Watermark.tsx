import React from 'react';
import {theme} from '../theme';

export const Watermark: React.FC = () => (
  <div
    style={{
      position: 'absolute',
      top: 90,
      left: 0,
      right: 0,
      display: 'flex',
      justifyContent: 'center',
      fontFamily: '"JetBrains Mono", monospace',
      fontSize: 28,
      letterSpacing: '0.18em',
      color: theme.textSecondary,
      opacity: 0.85,
      textShadow: '0 1px 3px rgba(0,0,0,0.8)',
    }}
  >
    FULLCARTS.ORG
  </div>
);
