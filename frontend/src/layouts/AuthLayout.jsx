import { Logo } from '../components/ui';

export default function AuthLayout({
  quote,
  gradient,
  backgroundImage,
  panel,
  children,
}) {
  return (
    <div className="flex min-h-screen bg-white">
      {/* Left side: Login form */}
      <div className="flex w-full flex-col px-6 py-8 md:w-1/2 md:px-14">
        <Logo />

        <div className="mx-auto flex w-full max-w-sm flex-1 flex-col justify-center py-8">
          {children}
        </div>
      </div>

      {/* Right side: Temple Night canvas or travel image */}
      {panel ? (
        <div className="relative hidden flex-1 overflow-hidden md:block" aria-hidden="true">
          {panel}
          {/* Quote overlay */}
          <div className="pointer-events-none absolute inset-0 flex items-start justify-center p-12">
            <p className="relative z-10 mt-10 whitespace-pre-line text-center font-script text-4xl leading-snug text-white drop-shadow-lg">
              {quote}
            </p>
          </div>
          {/* Bottom gradient for quote readability */}
          <div className="pointer-events-none absolute inset-x-0 bottom-0 h-1/2 bg-gradient-to-t from-slate-900/60 to-transparent" />
        </div>
      ) : (
        <div
          className={`relative hidden flex-1 items-start justify-center overflow-hidden bg-gradient-to-b p-12 md:flex ${
            backgroundImage ? '' : gradient || ''
          }`}
          style={
            backgroundImage
              ? {
                  backgroundImage: `url("${backgroundImage}")`,
                  backgroundSize: 'cover',
                  backgroundPosition: 'center',
                }
              : undefined
          }
          aria-hidden="true"
        >
          {/* Dark overlay for quote readability */}
          {backgroundImage && (
            <div className="absolute inset-0 bg-slate-900/30" />
          )}

          <p className="relative z-10 mt-10 whitespace-pre-line text-center font-script text-4xl leading-snug text-white drop-shadow-lg">
            {quote}
          </p>

          {/* Bottom gradient overlay */}
          <div className="absolute inset-x-0 bottom-0 h-1/2 bg-gradient-to-t from-slate-900/50 to-transparent" />
        </div>
      )}
    </div>
  );
}
