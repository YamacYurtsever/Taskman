import { GoogleLogoIcon } from '../components/icons';
import { api } from '../lib/api';
import styles from './LoginView.module.css';

const LoginView = () => {
  const handleSignIn = async () => {
    const res = await api.oauthStart();
    if (res?.url) {
      window.location.href = res.url;
    }
  };

  return (
    <div className={styles.page}>
      <div className={styles.mesh} aria-hidden="true" />

      <section className={styles.hero}>
        <div className={styles.copyBlock}>
          <p className={styles.eyebrow}>Your Private workspace</p>
          <h1 className={styles.title}>Taskman</h1>
          <p className={styles.tagline}>
            Have clarity. Build momentum. Get results.
          </p>
          <div className={styles.featureRow}>
            <span className={styles.featurePill}>Tasks</span>
            <span className={styles.featurePill}>Daysheet</span>
            <span className={styles.featurePill}>Calendar</span>
          </div>
        </div>

        <div className={styles.card}>
          <div className={styles.cardGlow} aria-hidden="true" />
          <div className={styles.cardHeader}>
            <span className={styles.cardKicker}>Sign in</span>
            <p className={styles.cardText}>
              Sign in with Google to start your journey.
            </p>
          </div>
          <button className={styles.signInBtn} onClick={handleSignIn}>
            <GoogleLogoIcon size={18} />
            Sign in with Google
          </button>
        </div>
      </section>
    </div>
  );
};

export { LoginView };
