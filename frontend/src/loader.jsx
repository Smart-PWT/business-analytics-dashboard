const Loader = () => {
  return (
    <div className="loader-container">
      <style>{`
        .abstract-graphic {
          width: 300px;
          height: 300px;
          animation: float 6s ease-in-out infinite;
        }

        @keyframes float {
          0% { transform: translateY(0px); }
          50% { transform: translateY(-10px); }
          100% { transform: translateY(0px); }
        }

        .spin-slow {
          transform-origin: 200px 200px;
          animation: spin 20s linear infinite;
        }

        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
      <svg viewBox="0 0 400 400" className="abstract-graphic">
        <circle cx="200" cy="200" r="140" stroke="#111" strokeWidth="1.5" fill="none" />
        
        <g className="spin-slow">
          <line x1="200" y1="60" x2="200" y2="340" stroke="#111" strokeWidth="1" transform="rotate(15 200 200)" />
          <line x1="60" y1="200" x2="340" y2="200" stroke="#111" strokeWidth="1" transform="rotate(15 200 200)" />
          <line x1="101" y1="101" x2="299" y2="299" stroke="#111" strokeWidth="1" transform="rotate(25 200 200)" />
        </g>
        
        <rect x="90" y="170" width="220" height="45" fill="#0b2d69" stroke="#111" strokeWidth="2" transform="rotate(-45 200 200)" />
        
        <rect x="180" y="130" width="130" height="35" fill="#8c6111" stroke="#111" strokeWidth="2" transform="rotate(-12 245 147)" />
        
        <rect x="80" y="270" width="22" height="22" fill="#222" transform="rotate(-15 91 281)" />
        
        <circle cx="310" cy="110" r="10" fill="#c81c1c" />
        
      </svg>
    </div>
  );
}

export default Loader;
