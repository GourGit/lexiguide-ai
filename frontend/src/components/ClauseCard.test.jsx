import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import ClauseCard from './ClauseCard';

describe('ClauseCard Component', () => {
  it('renders the clause text and explanation', () => {
    const mockClause = {
      text: "This agreement shall be governed by the laws of New York.",
      explanation: "New York law applies to this contract.",
      id: "clause-1"
    };

    render(<ClauseCard clause={mockClause} />);
    
    // Check if the original text is rendered
    expect(screen.getByText(/governed by the laws of New York/i)).toBeInTheDocument();
    
    // Check if the explanation is rendered
    expect(screen.getByText(/New York law applies to this contract/i)).toBeInTheDocument();
  });
});
