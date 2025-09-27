import React from "react";

export function DropAndChatLogoSVG({
  className,
  width = 32,
  height = 32
}: {
  className?: string;
  width?: number;
  height?: number;
}) {
  return (
    <svg
      className={className}
      width={width}
      height={height}
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <rect width="32" height="32" rx="8" fill="#2563eb" />
      <text
        x="16"
        y="18"
        textAnchor="middle"
        fontSize="8"
        fontWeight="bold"
        fill="white"
      >
        D&C
      </text>
    </svg>
  );
}

// Keep the old export for backward compatibility during transition
export const DropChatLogoSVG = DropAndChatLogoSVG;