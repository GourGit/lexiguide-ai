import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import ClauseCard from './ClauseCard';

describe('ClauseCard Component', () => {
  it('renders the clause text and explanation', () => {
    const mockClause = {
      original_text: "This agreement shall be governed by the laws of New York.",
      plain_explanation: "New York law applies to this contract.",
      clause_type: "Governing Law",
      id: "clause-1"
    };

    render(<ClauseCard clause={mockClause} />);
    
    // Check if the title is rendered
    expect(screen.getByText(/Governing Law/i)).toBeInTheDocument();
    
  });
});
