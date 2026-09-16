import { render, screen } from '@testing-library/react';
import RiskBadge from './RiskBadge';

describe('RiskBadge', () => {
  it('renders correctly for high risk', () => {
    render(<RiskBadge level="high" />);
    expect(screen.getByText('High')).toBeInTheDocument();
  });

  it('renders correctly for medium risk', () => {
    render(<RiskBadge level="medium" />);
    expect(screen.getByText('Medium')).toBeInTheDocument();
  });

  it('renders correctly for low risk', () => {
    render(<RiskBadge level="low" />);
    expect(screen.getByText('Low')).toBeInTheDocument();
  });

  it('renders correctly for standard risk', () => {
    render(<RiskBadge level="standard" />);
    expect(screen.getByText('Standard')).toBeInTheDocument();
  });
});
