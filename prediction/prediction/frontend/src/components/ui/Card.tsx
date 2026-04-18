import React from 'react';

/**
 * Card component - Reusable container for grouped content
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - Card content
 * @param {string} props.title - Card title
 * @param {string} props.subtitle - Card subtitle
 * @param {string} props.className - Additional CSS classes
 * @param {string} props.id - Card ID
 */

interface CardProps {
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
  className?: string;
  id?: string;
}

const Card: React.FC<CardProps> = ({
  title,
  subtitle,
  className = '',
  children,
  id = ''
}) => {
  return (
    <section className={`card ${className}`.trim()} id={id}>
      {title && <h2 className="card-title">{title}</h2>}
      {subtitle && <p className="card-subtitle">{subtitle}</p>}
      <div className="card-content">{children}</div>
    </section>
  );
};

export default Card;
