
import React from 'react'
import './petitioncontainer.css'
// maybe...
// https://tanstack.com/query/latest/docs/react/reference/useInfiniteQuery

`use client`

export default function PetitionEmpty() {
    return (
        <div className={`petitions-outer`}>
            <ul className={`petitions-container`}>
                <p>No petitions found!</p>
            </ul>
        </div>
    )
}
