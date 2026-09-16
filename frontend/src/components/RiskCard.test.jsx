import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import RiskCard from './RiskCard';

describe('RiskCard Component', () => {
  it('renders a high risk correctly', () => {
    const mockRisk = {
      level: "High",
      explanation: "This clause severely limits your ability to sue.",
      lawyer_question: "Should we negotiate a cap on this liability limit?"
    };

    render(<RiskCard risk={mockRisk} index={1} />);
    
    // Check if the explanation is rendered
    expect(screen.getByText(/severely limits your ability to sue/i)).toBeInTheDocument();
    
    // Check if the lawyer question is rendered
    expect(screen.getByText(/Should we negotiate a cap/i)).toBeInTheDocument();
  });
});
