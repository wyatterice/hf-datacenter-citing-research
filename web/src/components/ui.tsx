// Small form primitives styled with the CIR brand tokens.

import type { CSSProperties, ReactNode } from 'react'

interface ControlsRowProps {
  children: ReactNode
  cols?: number
}

// A responsive row of form fields, styled to sit on the CIR canvas.
export function SegmentedControlRow({ children, cols = 2 }: ControlsRowProps) {
  return (
    <div className="dc-controls-row" style={{ '--dc-cols': cols } as CSSProperties}>
      {children}
    </div>
  )
}

interface FieldProps {
  label: string
  children: ReactNode
  hint?: string
}

export function Field({ label, children, hint }: FieldProps) {
  return (
    <div className="dc-field">
      <span className="dc-field-label">{label}</span>
      {children}
      {hint ? <span className="dc-field-hint">{hint}</span> : null}
    </div>
  )
}

interface SelectProps {
  value: string
  options: { value: string; label: string }[]
  onChange: (value: string) => void
}

export function Select({ value, options, onChange }: SelectProps) {
  return (
    <select className="dc-select" value={value} onChange={(e) => onChange(e.target.value)}>
      {options.map((o) => (
        <option key={o.value} value={o.value}>
          {o.label}
        </option>
      ))}
    </select>
  )
}

interface SegmentedProps<T extends string> {
  value: T
  options: { value: T; label: string }[]
  onChange: (value: T) => void
  disabled?: boolean
}

// Segmented radio built on the CIR .time-range-selector / .time-range-btn look.
export function Segmented<T extends string>({ value, options, onChange, disabled }: SegmentedProps<T>) {
  return (
    <div className={`time-range-selector dc-segmented${disabled ? ' dc-disabled' : ''}`} role="radiogroup">
      {options.map((o) => (
        <button
          key={o.value}
          type="button"
          role="radio"
          aria-checked={value === o.value}
          className={`time-range-btn${value === o.value ? ' active' : ''}`}
          disabled={disabled}
          onClick={() => onChange(o.value)}
        >
          {o.label}
        </button>
      ))}
    </div>
  )
}

interface NumberFieldProps {
  value: number | null
  onChange: (value: number | null) => void
  min?: number
  max?: number
  step?: number
  placeholder?: string
  allowEmpty?: boolean
}

export function NumberField({ value, onChange, min, max, step, placeholder, allowEmpty }: NumberFieldProps) {
  return (
    <input
      className="dc-input"
      type="number"
      value={value ?? ''}
      min={min}
      max={max}
      step={step}
      placeholder={placeholder}
      onChange={(e) => {
        const raw = e.target.value
        if (raw === '') {
          onChange(allowEmpty ? null : min ?? 0)
          return
        }
        onChange(Number(raw))
      }}
    />
  )
}

interface SliderFieldProps {
  value: number
  onChange: (value: number) => void
  min: number
  max: number
  step?: number
  suffix?: string
}

export function SliderField({ value, onChange, min, max, step = 1, suffix }: SliderFieldProps) {
  return (
    <div className="dc-slider">
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
      />
      <span className="dc-slider-value">
        {value}
        {suffix}
      </span>
    </div>
  )
}
