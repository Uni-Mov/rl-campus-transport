import { useState } from "react";

interface AddressInputProps {
  onAddPoint: (address: string) => void;
  isGeocoding: boolean;
  error: string | null;
}

export const AddressInput = ({ onAddPoint, isGeocoding, error }: AddressInputProps) => {
  const [addressInput, setAddressInput] = useState("");

  const handleAddFromAddress = () => {
    if (addressInput.trim()) {
      onAddPoint(addressInput.trim());
      setAddressInput("");
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleAddFromAddress();
    }
  };

  return (
    <div className="mb-3">
      <label className="block text-sm font-medium text-gray-700 mb-1">
        O ingresa una dirección:
      </label>
      <div className="flex gap-2">
        <input
          type="text"
          value={addressInput}
          onChange={(e) => setAddressInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ej: Av. Corrientes 1234, Buenos Aires"
          className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          disabled={isGeocoding}
        />
        <button
          onClick={handleAddFromAddress}
          disabled={!addressInput.trim() || isGeocoding}
          className={`
            px-3 py-2 rounded-md text-sm font-medium transition-colors
            ${addressInput.trim() && !isGeocoding
              ? 'bg-blue-600 hover:bg-blue-700 text-white'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }
          `}
        >
          {isGeocoding ? '...' : 'Buscar'}
        </button>
      </div>
      {error && (
        <p className="text-red-500 text-xs mt-1">{error}</p>
      )}
    </div>
  );
};

