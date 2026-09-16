import { render, screen } from '@testing-library/react';
import RiskBadge from './RiskBadge';

describe('RiskBadge', () => {
  it('renders correctly for high risk', () => {
    render(<RiskBadge level="high" />);
    expect(screen.getByText('High attention')).toBeInTheDocument();
  });

  it('renders correctly for medium risk', () => {
    render(<RiskBadge level="medium" />);
    expect(screen.getByText('Review carefully')).toBeInTheDocument();
  });

  it('renders correctly for low risk', () => {
    render(<RiskBadge level="low" />);
    expect(screen.getByText('Worth checking')).toBeInTheDocument();
  });

  it('renders correctly for standard risk', () => {
    render(<RiskBadge level="standard" />);
    expect(screen.getByText('Standard')).toBeInTheDocument();
  });
});
