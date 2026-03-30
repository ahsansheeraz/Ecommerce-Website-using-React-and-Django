import React from 'react';
import { HiOutlineShoppingBag, HiOutlineLocationMarker, HiOutlineCreditCard, HiOutlineCheckCircle } from 'react-icons/hi';

const CheckoutSteps = ({ currentStep }) => {
  const steps = [
    { number: 1, name: 'Cart', icon: HiOutlineShoppingBag },
    { number: 2, name: 'Shipping', icon: HiOutlineLocationMarker },
    { number: 3, name: 'Payment', icon: HiOutlineCreditCard },
    { number: 4, name: 'Confirmation', icon: HiOutlineCheckCircle }
  ];

  return (
    <div className="mb-8">
      <div className="flex items-center justify-between">
        {steps.map((step, index) => {
          const Icon = step.icon;
          const isActive = step.number === currentStep;
          const isComplete = step.number < currentStep;
          
          return (
            <React.Fragment key={step.number}>
              {/* Step Item */}
              <div className="flex flex-col items-center">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center transition-all ${
                    isActive
                      ? 'bg-primary-600 text-white scale-110 shadow-lg'
                      : isComplete
                      ? 'bg-green-500 text-white'
                      : 'bg-gray-200 text-gray-500'
                  }`}
                >
                  {isComplete ? (
                    <HiOutlineCheckCircle className="w-5 h-5" />
                  ) : (
                    <Icon className="w-5 h-5" />
                  )}
                </div>
                <span
                  className={`text-xs mt-2 font-medium ${
                    isActive ? 'text-primary-600' : 'text-gray-500'
                  }`}
                >
                  {step.name}
                </span>
              </div>

              {/* Connector Line */}
              {index < steps.length - 1 && (
                <div
                  className={`flex-1 h-1 mx-2 transition-all ${
                    step.number < currentStep ? 'bg-green-500' : 'bg-gray-200'
                  }`}
                />
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
};

export default CheckoutSteps;