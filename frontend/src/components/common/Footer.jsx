import React from 'react';
import { Link } from 'react-router-dom';
import { 
  HiOutlineMail, 
  HiOutlinePhone, 
  HiOutlineLocationMarker,
  HiOutlineHeart,
  HiOutlineShoppingBag,
  HiOutlineShieldCheck
} from 'react-icons/hi';
import { 
  FaFacebook, 
  FaTwitter, 
  FaInstagram, 
  FaLinkedin,
  FaYoutube 
} from 'react-icons/fa';

const Footer = () => {
  const footerLinks = {
    company: [
      { name: 'About Us', path: '/about' },
      { name: 'Careers', path: '/careers' },
      { name: 'Press', path: '/press' },
      { name: 'Blog', path: '/blog' },
    ],
    support: [
      { name: 'Help Center', path: '/help' },
      { name: 'Contact Us', path: '/contact' },
      { name: 'Returns', path: '/returns' },
      { name: 'Shipping Info', path: '/shipping' },
    ],
    legal: [
      { name: 'Privacy Policy', path: '/privacy' },
      { name: 'Terms of Service', path: '/terms' },
      { name: 'Cookie Policy', path: '/cookies' },
      { name: 'FAQs', path: '/faqs' },
    ],
  };

  const features = [
    { icon: HiOutlineShoppingBag, text: 'Free Shipping on $50+' },
    { icon: HiOutlineHeart, text: '10,000+ Happy Customers' },
    { icon: HiOutlineShieldCheck, text: '100% Secure Payment' },
  ];

  const socialLinks = [
    { icon: FaFacebook, href: 'https://facebook.com', color: 'hover:text-blue-600' },
    { icon: FaTwitter, href: 'https://twitter.com', color: 'hover:text-blue-400' },
    { icon: FaInstagram, href: 'https://instagram.com', color: 'hover:text-pink-600' },
    { icon: FaLinkedin, href: 'https://linkedin.com', color: 'hover:text-blue-700' },
    { icon: FaYoutube, href: 'https://youtube.com', color: 'hover:text-red-600' },
  ];

  return (
    <footer className="bg-white border-t">
      {/* Features Bar */}
      <div className="bg-gradient-to-r from-primary-50 to-primary-100 py-8">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <div key={index} className="flex items-center justify-center space-x-3">
                <feature.icon className="w-8 h-8 text-primary-600" />
                <span className="text-gray-700 font-medium">{feature.text}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Main Footer */}
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8">
          {/* Brand */}
          <div className="lg:col-span-1">
            <Link to="/" className="flex items-center space-x-2 mb-6">
              <div className="w-10 h-10 bg-gradient-to-r from-primary-500 to-primary-700 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xl">E</span>
              </div>
              <span className="text-2xl font-bold bg-gradient-to-r from-primary-600 to-primary-800 bg-clip-text text-transparent">
                Mart
              </span>
            </Link>
            <p className="text-gray-600 mb-6">
              Your one-stop destination for quality products at the best prices.
            </p>
            <div className="space-y-3">
              <div className="flex items-center space-x-3 text-gray-600">
                <HiOutlineLocationMarker className="w-5 h-5 text-primary-600" />
                <span>123 Business Ave, Suite 100</span>
              </div>
              <div className="flex items-center space-x-3 text-gray-600">
                <HiOutlinePhone className="w-5 h-5 text-primary-600" />
                <span>+1 (555) 123-4567</span>
              </div>
              <div className="flex items-center space-x-3 text-gray-600">
                <HiOutlineMail className="w-5 h-5 text-primary-600" />
                <span>support@emart.com</span>
              </div>
            </div>
          </div>

          {/* Links */}
          <div className="lg:col-span-3 grid grid-cols-1 sm:grid-cols-3 gap-8">
            <div>
              <h3 className="font-semibold text-gray-900 mb-4">Company</h3>
              <ul className="space-y-3">
                {footerLinks.company.map((link) => (
                  <li key={link.name}>
                    <Link
                      to={link.path}
                      className="text-gray-600 hover:text-primary-600 transition-colors"
                    >
                      {link.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 mb-4">Support</h3>
              <ul className="space-y-3">
                {footerLinks.support.map((link) => (
                  <li key={link.name}>
                    <Link
                      to={link.path}
                      className="text-gray-600 hover:text-primary-600 transition-colors"
                    >
                      {link.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 mb-4">Legal</h3>
              <ul className="space-y-3">
                {footerLinks.legal.map((link) => (
                  <li key={link.name}>
                    <Link
                      to={link.path}
                      className="text-gray-600 hover:text-primary-600 transition-colors"
                    >
                      {link.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Newsletter */}
          <div className="lg:col-span-1">
            <h3 className="font-semibold text-gray-900 mb-4">Subscribe</h3>
            <p className="text-gray-600 mb-4">
              Get updates about new products and special offers.
            </p>
            <form className="space-y-3">
              <input
                type="email"
                placeholder="Your email"
                className="input-primary"
              />
              <button type="submit" className="btn-primary w-full">
                Subscribe
              </button>
            </form>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t mt-12 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <p className="text-gray-600 text-sm mb-4 md:mb-0">
              © 2024 E-Mart. All rights reserved.
            </p>
            <div className="flex space-x-6">
              {socialLinks.map((social, index) => (
                <a
                  key={index}
                  href={social.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={`text-gray-400 ${social.color} transition-colors`}
                >
                  <social.icon className="w-5 h-5" />
                </a>
              ))}
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;