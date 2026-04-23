import type { Role } from "./Role";
import type { Committee } from "./Committee";

export type UserProfile = {
  username: string;
  first_name: string;
  last_name: string;
  roles: Role[];
  committees: Committee[] | null;
};
