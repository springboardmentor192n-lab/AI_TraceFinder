import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Eye, EyeOff, Mail, Lock, User, Chrome, Facebook } from 'lucide-react';

const Auth = ({ setIsAuthenticated }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    confirmPassword: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Store auth state
    localStorage.setItem('tracefinder-auth', 'true');
    localStorage.setItem('tracefinder-user', JSON.stringify({
      email: formData.email,
      name: formData.name || formData.email.split('@')[0]
    }));
    
    setIsAuthenticated(true);
    setIsLoading(false);
    navigate('/');
  };

  const handleGoogleLogin = async () => {
    setIsLoading(true);
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    localStorage.setItem('tracefinder-auth', 'true');
    localStorage.setItem('tracefinder-user', JSON.stringify({
      email: 'user@gmail.com',
      name: 'Google User',
      avatar: 'https://lh3.googleusercontent.com/a/default-user'
    }));
    
    setIsAuthenticated(true);
    setIsLoading(false);
    navigate('/');
  };

  const handleFacebookLogin = async () => {
    setIsLoading(true);
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    localStorage.setItem('tracefinder-auth', 'true');
    localStorage.setItem('tracefinder-user', JSON.stringify({
      email: 'user@facebook.com',
      name: 'Facebook User',
      avatar: 'https://graph.facebook.com/default-user/picture'
    }));
    
    setIsAuthenticated(true);
    setIsLoading(false);
    navigate('/');
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #f9f8ff 0%, #eef0ff 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px'
    }}>
      <div style={{
        backgroundColor: 'white',
        borderRadius: '24px',
        boxShadow: '0 18px 45px rgba(91, 95, 199, 0.12)',
        padding: '40px',
        width: '100%',
        maxWidth: '480px',
        border: '1px solid var(--border)'
      }}>
        {/* Logo */}
        <div style={{ textAlign: 'center', marginBottom: '32px', cursor: 'pointer' }} onClick={() => navigate('/')}>
          <div style={{
            width: '64px',
            height: '64px',
            borderRadius: '16px',
            background: 'linear-gradient(135deg, #5b5fc7 0%, #4a90d9 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontSize: '1.8rem',
            margin: '0 auto 16px'
          }}>
            🔬
          </div>
          <h1 style={{ margin: 0, fontSize: '1.8rem', color: 'var(--text)' }}>
            TraceFinder
          </h1>
          <p style={{ margin: '8px 0 0', color: 'var(--muted)', fontSize: '0.9rem' }}>
            Document Forensic Intelligence
          </p>
        </div>

        {/* Tab Toggle */}
        <div style={{
          display: 'flex',
          backgroundColor: 'var(--surface-soft)',
          borderRadius: '12px',
          padding: '4px',
          marginBottom: '32px'
        }}>
          <button
            style={{
              flex: 1,
              padding: '12px',
              border: 'none',
              borderRadius: '8px',
              backgroundColor: isLogin ? 'white' : 'transparent',
              color: isLogin ? 'var(--text)' : 'var(--muted)',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
            onClick={() => setIsLogin(true)}
          >
            Sign In
          </button>
          <button
            style={{
              flex: 1,
              padding: '12px',
              border: 'none',
              borderRadius: '8px',
              backgroundColor: !isLogin ? 'white' : 'transparent',
              color: !isLogin ? 'var(--text)' : 'var(--muted)',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
            onClick={() => setIsLogin(false)}
          >
            Sign Up
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit}>
          {!isLogin && (
            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500', color: 'var(--text)' }}>
                <User size={16} style={{ display: 'inline', marginRight: '8px', verticalAlign: 'middle' }} />
                Full Name
              </label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                required={!isLogin}
                placeholder="Enter your full name"
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  border: '1px solid var(--border)',
                  borderRadius: '12px',
                  fontSize: '0.9rem',
                  backgroundColor: 'var(--surface-soft)'
                }}
              />
            </div>
          )}

          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500', color: 'var(--text)' }}>
              <Mail size={16} style={{ display: 'inline', marginRight: '8px', verticalAlign: 'middle' }} />
              Email Address
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              required
              placeholder="Enter your email"
              style={{
                width: '100%',
                padding: '12px 16px',
                border: '1px solid var(--border)',
                borderRadius: '12px',
                fontSize: '0.9rem',
                backgroundColor: 'var(--surface-soft)'
              }}
            />
          </div>

          <div style={{ marginBottom: '24px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500', color: 'var(--text)' }}>
              <Lock size={16} style={{ display: 'inline', marginRight: '8px', verticalAlign: 'middle' }} />
              Password
            </label>
            <div style={{ position: 'relative' }}>
              <input
                type={showPassword ? 'text' : 'password'}
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                required
                placeholder="Enter your password"
                style={{
                  width: '100%',
                  padding: '12px 44px 12px 16px',
                  border: '1px solid var(--border)',
                  borderRadius: '12px',
                  fontSize: '0.9rem',
                  backgroundColor: 'var(--surface-soft)'
                }}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                style={{
                  position: 'absolute',
                  right: '12px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  border: 'none',
                  background: 'none',
                  cursor: 'pointer',
                  color: 'var(--muted)'
                }}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          {!isLogin && (
            <div style={{ marginBottom: '24px' }}>
              <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500', color: 'var(--text)' }}>
                Confirm Password
              </label>
              <input
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleInputChange}
                required={!isLogin}
                placeholder="Confirm your password"
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  border: '1px solid var(--border)',
                  borderRadius: '12px',
                  fontSize: '0.9rem',
                  backgroundColor: 'var(--surface-soft)'
                }}
              />
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            style={{
              width: '100%',
              padding: '14px',
              border: 'none',
              borderRadius: '12px',
              background: 'linear-gradient(135deg, #5b5fc7, #6f69ff)',
              color: 'white',
              fontSize: '1rem',
              fontWeight: '600',
              cursor: isLoading ? 'not-allowed' : 'pointer',
              opacity: isLoading ? 0.7 : 1,
              transition: 'all 0.2s ease'
            }}
          >
            {isLoading ? (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                <div style={{
                  width: '16px',
                  height: '16px',
                  border: '2px solid #fff',
                  borderTop: '2px solid transparent',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite'
                }}></div>
                {isLogin ? 'Signing In...' : 'Creating Account...'}
              </div>
            ) : (
              isLogin ? 'Sign In' : 'Sign Up'
            )}
          </button>
        </form>

        {/* Divider */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          margin: '32px 0',
          gap: '16px'
        }}>
          <div style={{ flex: 1, height: '1px', backgroundColor: 'var(--border)' }}></div>
          <span style={{ color: 'var(--muted)', fontSize: '0.9rem' }}>OR</span>
          <div style={{ flex: 1, height: '1px', backgroundColor: 'var(--border)' }}></div>
        </div>

        {/* Social Login */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <button
            onClick={handleGoogleLogin}
            disabled={isLoading}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '12px',
              padding: '12px',
              border: '1px solid var(--border)',
              borderRadius: '12px',
              backgroundColor: 'white',
              cursor: isLoading ? 'not-allowed' : 'pointer',
              opacity: isLoading ? 0.7 : 1,
              transition: 'all 0.2s ease'
            }}
          >
            <Chrome size={20} style={{ color: '#4285f4' }} />
            <span style={{ fontWeight: '500' }}>Continue with Google</span>
          </button>

          <button
            onClick={handleFacebookLogin}
            disabled={isLoading}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '12px',
              padding: '12px',
              border: '1px solid var(--border)',
              borderRadius: '12px',
              backgroundColor: 'white',
              cursor: isLoading ? 'not-allowed' : 'pointer',
              opacity: isLoading ? 0.7 : 1,
              transition: 'all 0.2s ease'
            }}
          >
            <Facebook size={20} style={{ color: '#1877f2' }} />
            <span style={{ fontWeight: '500' }}>Continue with Facebook</span>
          </button>
        </div>

        {/* Terms */}
        <p style={{
          textAlign: 'center',
          fontSize: '0.8rem',
          color: 'var(--muted)',
          marginTop: '24px',
          lineHeight: 1.4
        }}>
          By continuing, you agree to our{' '}
          <a href="#" style={{ color: 'var(--primary)', textDecoration: 'none' }}>Terms of Service</a>
          {' '}and{' '}
          <a href="#" style={{ color: 'var(--primary)', textDecoration: 'none' }}>Privacy Policy</a>
        </p>
      </div>

      <style jsx>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default Auth;
