export type AuthorType = {
  username: string;
  first_name: string;
  last_name: string;
  roles: any[];
};


export function getAuthorName(author: AuthorType | null | undefined): string {
  if (!author) return "Unknown";

  const first = author.first_name?.trim();
  const last = author.last_name?.trim();

  if (first || last) {
    return `${first ?? ""} ${last ?? ""}`.trim();
  }

  return author.username ?? "Unknown";
}
