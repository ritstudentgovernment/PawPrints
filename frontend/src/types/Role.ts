import type { Permission } from "./Permission";

export type Role = {
  id: number | null;
  name: string;
  description?: string | null;
  permissions?: Permission[] | null;
};
