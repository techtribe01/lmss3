import React from 'react';
import { motion } from 'framer-motion';
import './SkeletonLoader.css';

export const SkeletonCard = () => (
  <motion.div 
    className="skeleton-card"
    initial={{ opacity: 1 }}
    exit={{ opacity: 0 }}
    transition={{ duration: 0.3 }}
  >
    <div className="skeleton-image"></div>
    <div className="skeleton-body">
      <div className="skeleton-line skeleton-title"></div>
      <div className="skeleton-line skeleton-text"></div>
      <div className="skeleton-line skeleton-text-short"></div>
    </div>
  </motion.div>
);

export const SkeletonTable = ({ rows = 5, columns = 6 }) => (
  <motion.div 
    className="skeleton-table"
    initial={{ opacity: 1 }}
    exit={{ opacity: 0 }}
    transition={{ duration: 0.3 }}
  >
    <div className="skeleton-table-header">
      {Array.from({ length: columns }).map((_, i) => (
        <div key={i} className="skeleton-line"></div>
      ))}
    </div>
    {Array.from({ length: rows }).map((_, rowIndex) => (
      <div key={rowIndex} className="skeleton-table-row">
        {Array.from({ length: columns }).map((_, colIndex) => (
          <div key={colIndex} className="skeleton-line"></div>
        ))}
      </div>
    ))}
  </motion.div>
);

export const SkeletonStat = () => (
  <motion.div 
    className="skeleton-stat"
    initial={{ opacity: 1 }}
    exit={{ opacity: 0 }}
    transition={{ duration: 0.3 }}
  >
    <div className="skeleton-circle"></div>
    <div className="skeleton-stat-content">
      <div className="skeleton-line skeleton-text-short"></div>
      <div className="skeleton-line skeleton-title"></div>
    </div>
  </motion.div>
);

export const SkeletonList = ({ items = 5 }) => (
  <motion.div 
    className="skeleton-list"
    initial={{ opacity: 1 }}
    exit={{ opacity: 0 }}
    transition={{ duration: 0.3 }}
  >
    {Array.from({ length: items }).map((_, i) => (
      <div key={i} className="skeleton-list-item">
        <div className="skeleton-circle-sm"></div>
        <div className="skeleton-list-content">
          <div className="skeleton-line"></div>
          <div className="skeleton-line skeleton-text-short"></div>
        </div>
      </div>
    ))}
  </motion.div>
);
