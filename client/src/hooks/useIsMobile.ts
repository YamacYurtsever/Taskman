import { useEffect, useState } from 'react';

const MOBILE_MEDIA = '(max-width: 780px)';

export const useIsMobile = () => {
  const getMatches = () =>
    typeof window !== 'undefined' && window.matchMedia(MOBILE_MEDIA).matches;

  const [isMobile, setIsMobile] = useState(getMatches);

  useEffect(() => {
    const mediaQuery = window.matchMedia(MOBILE_MEDIA);
    const onChange = (event: MediaQueryListEvent) => setIsMobile(event.matches);

    setIsMobile(mediaQuery.matches);
    mediaQuery.addEventListener('change', onChange);

    return () => mediaQuery.removeEventListener('change', onChange);
  }, []);

  return isMobile;
};
