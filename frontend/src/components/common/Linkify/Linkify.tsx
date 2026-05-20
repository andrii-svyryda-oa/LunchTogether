import { Fragment } from "react";

const URL_REGEX = /(https?:\/\/[^\s<>"']+|www\.[^\s<>"']+)/gi;

function stripTrailingPunctuation(url: string): {
  url: string;
  trailing: string;
} {
  const match = url.match(/[).,;:!?]+$/);
  if (!match) return { url, trailing: "" };
  return {
    url: url.slice(0, -match[0].length),
    trailing: match[0],
  };
}

function normalizeHref(url: string): string {
  return url.startsWith("www.") ? `https://${url}` : url;
}

interface LinkifyProps {
  text: string;
  className?: string;
}

export function Linkify({ text, className }: LinkifyProps) {
  const parts: React.ReactNode[] = [];
  let lastIndex = 0;
  let match: RegExpExecArray | null;
  URL_REGEX.lastIndex = 0;

  while ((match = URL_REGEX.exec(text)) !== null) {
    const start = match.index;
    const raw = match[0];
    const { url, trailing } = stripTrailingPunctuation(raw);

    if (start > lastIndex) {
      parts.push(text.slice(lastIndex, start));
    }

    parts.push(
      <a
        key={start}
        href={normalizeHref(url)}
        target="_blank"
        rel="noreferrer noopener"
        className="text-primary underline-offset-2 hover:underline break-all"
      >
        {url}
      </a>,
    );

    if (trailing) parts.push(trailing);

    lastIndex = start + raw.length;
  }

  if (lastIndex < text.length) {
    parts.push(text.slice(lastIndex));
  }

  return (
    <span className={className}>
      {parts.map((part, i) => (
        <Fragment key={i}>{part}</Fragment>
      ))}
    </span>
  );
}
