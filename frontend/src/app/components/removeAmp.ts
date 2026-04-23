export function removeAmp(text: string): string {
    return text.replace(/&amp;|&/g, ' & ').trim();
}