import * as React from "react"
import { cn } from "@/lib/utils"

interface ScrollShadowProps extends React.HTMLAttributes<HTMLDivElement> {
  className?: string
  containerClassName?: string
  hideScrollbar?: boolean
}

export function ScrollShadow({
  className,
  containerClassName,
  hideScrollbar = false,
  children,
  ...props
}: ScrollShadowProps) {
  const contentRef = React.useRef<HTMLDivElement>(null)
  const [showTopShadow, setShowTopShadow] = React.useState(false)
  const [showBottomShadow, setShowBottomShadow] = React.useState(false)

  const handleScroll = React.useCallback(() => {
    if (!contentRef.current) return

    const { scrollTop, scrollHeight, clientHeight } = contentRef.current
    setShowTopShadow(scrollTop > 0)
    setShowBottomShadow(scrollTop < scrollHeight - clientHeight - 1)
  }, [])

  React.useEffect(() => {
    const content = contentRef.current
    if (!content) return

    handleScroll()
    content.addEventListener("scroll", handleScroll)
    window.addEventListener("resize", handleScroll)

    return () => {
      content.removeEventListener("scroll", handleScroll)
      window.removeEventListener("resize", handleScroll)
    }
  }, [handleScroll])

  return (
    <div
      className={cn(
        "relative",
        containerClassName
      )}
      {...props}
    >
      {/* Top shadow */}
      {showTopShadow && (
        <div className="absolute top-0 left-0 right-0 h-4 bg-gradient-to-b from-background to-transparent pointer-events-none z-10" />
      )}

      {/* Scrollable content */}
      <div
        ref={contentRef}
        className={cn(
          "overflow-y-auto",
          hideScrollbar && "scrollbar-hide",
          className
        )}
      >
        {children}
      </div>

      {/* Bottom shadow */}
      {showBottomShadow && (
        <div className="absolute bottom-0 left-0 right-0 h-4 bg-gradient-to-t from-background to-transparent pointer-events-none z-10" />
      )}
    </div>
  )
} 