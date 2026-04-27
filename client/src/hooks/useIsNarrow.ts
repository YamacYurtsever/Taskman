import { useEffect, useState } from 'react';

const NARROW_MEDIA = '(max-width: 1024px)';

export const useIsNarrow = () => {
  const getMatches = () =>
    typeof window !== 'undefined' && window.matchMedia(NARROW_MEDIA).matches;

  const [isNarrow, setIsNarrow] = useState(getMatches);

  useEffect(() => {
    const mediaQuery = window.matchMedia(NARROW_MEDIA);
    const onChange = (event: MediaQueryListEvent) => setIsNarrow(event.matches);

    setIsNarrow(mediaQuery.matches);
    mediaQuery.addEventListener('change', onChange);

    return () => mediaQuery.removeEventListener('change', onChange);
  }, []);

  return isNarrow;
};
