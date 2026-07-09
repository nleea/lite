import type { InputHTMLAttributes } from "react";

import { Input } from "@/components/atoms/Input";
import { Label } from "@/components/atoms/Label";

interface Props extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
}

export function FormField({ label, id, ...props }: Props) {
  return (
    <div>
      <Label htmlFor={id}>{label}</Label>
      <Input id={id} {...props} />
    </div>
  );
}
