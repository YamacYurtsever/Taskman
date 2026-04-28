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
      <h1 className={styles.title}>Taskman</h1>
      <p className={styles.tagline}>Your personal task manager</p>
      <button className={styles.signInBtn} onClick={handleSignIn}>
        <GoogleLogoIcon size={18} />
        Sign in with Google
      </button>
    </div>
  );
};

export { LoginView };
