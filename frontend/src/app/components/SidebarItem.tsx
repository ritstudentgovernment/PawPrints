
'use client'
import React from 'react'
import './sidebar.css'

export type TagType = {
    id: number;
    name: string;
    description: string;
    color: string;
}

export default function SidebarItem(item:TagType) {

    return (
        <option value={item.id}>{item.name}</option> 
    )
}