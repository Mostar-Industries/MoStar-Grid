import React, { useRef, useEffect, useState, useId } from 'react';

export function Sparkline({ data, width = 120, height = 28 }: { data: number[]; width?: number; height?: number }) {
    const pathRef = useRef<SVGPathElement>(null);
    const [pathLength, setPathLength] = useState(0);
    const id = useId();
    const gradientId = `sparkline-gradient-${id}`;

    useEffect(() => {
        if (pathRef.current) {
            const length = pathRef.current.getTotalLength();
            setPathLength(length);
        }
    }, [data, width, height]); // Recalculate if data or dimensions change

    if (!data || data.length < 2) {
        return <div style={{ width, height }} className="flex items-center justify-center text-gray-500 text-xs">...</div>;
    }

    const max = Math.max(...data);
    const min = Math.min(...data);
    const yPadding = 4;
    const effectiveHeight = height - yPadding * 2;

    const norm = (v: number) => {
        if (max === min) return yPadding + effectiveHeight / 2;
        // Invert y-axis for SVG
        return yPadding + effectiveHeight - (((v - min) / (max - min)) * effectiveHeight);
    };
    const step = width / Math.max(1, data.length - 1);
    // Fix: Corrected the order of operations. The multiplication should happen before converting to a fixed-point string.
    const pathData = data.map((v, i) => `${i === 0 ? "M" : "L"} ${(i * step).toFixed(2)} ${norm(v).toFixed(2)}`).join(" ");

    const areaData = `${pathData} L ${width} ${height} L 0 ${height} Z`;

    const animationStyle: React.CSSProperties = pathLength > 0 ? {
        strokeDasharray: pathLength,
        strokeDashoffset: pathLength,
        animation: `sparkline-draw 1.5s ease-out forwards`,
    } : {
        // Hide path until length is calculated to prevent flicker of un-animated line
        strokeDasharray: 1, 
        strokeDashoffset: 1,
    };

    return (
        <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Sparkline chart">
            <defs>
                <linearGradient id={gradientId} x1="0" x2="0" y1="0" y2="1">
                    <stop offset="0%" stopColor="currentColor" stopOpacity="0.2" />
                    <stop offset="100%" stopColor="currentColor" stopOpacity="0" />
                </linearGradient>
            </defs>
            <path
                d={areaData}
                fill={`url(#${gradientId})`}
                stroke="none"
            />
            <path
                ref={pathRef}
                d={pathData}
                fill="none"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
                style={animationStyle}
            />
        </svg>
    );
}