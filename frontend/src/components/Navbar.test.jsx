import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import Navbar from './Navbar';

describe('Navbar Component', () => {
  it('renders navigation links', () => {
    render(
      <BrowserRouter>
        <Navbar />
      </BrowserRouter>
    );
    
    // Check if the logo/home link is rendered
    expect(screen.getByText(/LexiGuide/i)).toBeInTheDocument();
    
    // Check if other links are rendered
    expect(screen.getByText(/Compare/i)).toBeInTheDocument();
    expect(screen.getByText(/Legal Information/i)).toBeInTheDocument();
  });
});
