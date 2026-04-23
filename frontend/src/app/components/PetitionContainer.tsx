import PetitionList from './PetitionList'
import { GET, GETTag } from '../api/specialRoute'

export default async function PetitionContainer({
    query,
    tag, 
    status
}: {
    query?: string
    tag?: string
    status?: string
}) {
    const PAGE = 1;
    const ITEMS = 40;

    let initialData = [];

    try {
        const result = await GET(query, status, tag, PAGE, ITEMS);
        initialData = result.petitions || [];
    } catch (err) {
        console.error("Error inside container:", err);
        initialData = [];
    }

    return (
        <div className="petitions-outer">
            <PetitionList 
                initialData={initialData} 
                query={query} 
                tag={tag} 
                status={status} 
            />
        </div>
    );
}