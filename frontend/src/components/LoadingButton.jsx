function LoadingButton({ children, isLoading, loadingText, ...props }) {
  return (
    <button className="primary-button" type="button" {...props}>
      {isLoading ? loadingText : children}
    </button>
  );
}

export default LoadingButton;
