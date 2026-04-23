'use client';

import './search.css'
import 'material-symbols';
import { useSearchParams, usePathname, useRouter} from 'next/navigation';
import { useDebouncedCallback } from 'use-debounce';
import Sidebar from './Sidebar';
import { TagType } from './SidebarItem';

export default function Search({ placeholder, tags }: { placeholder: string, tags: TagType[]}) {
    const searchParams = useSearchParams();
    const pathname = usePathname();
    const { replace } = useRouter();

    const handleSearch = useDebouncedCallback((term) => {

        const params = new URLSearchParams(searchParams);
        if (term) {
            params.set('query', term);
        } else {
            params.delete('query');
        }
        replace(`${pathname}?${params.toString()}`, {scroll: false});
    }, 700);

    return (
        <div className="search drop-shadow-md">
            <label htmlFor="search" className={`sr-only`}>
                Search
            </label>
            <div className={`material-icon-container`}>
                <span className="material-symbols-outlined">search</span> 
            </div>
            <input
                className={`input_box`}
                placeholder={placeholder}
                onChange={(e) => {
                    handleSearch(e.target.value);
                }}
                defaultValue={searchParams.get('query')?.toString()}
            />
            <Sidebar tags={tags}></Sidebar>
        </div>
    );
}