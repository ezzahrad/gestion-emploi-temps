// Table.tsx - Composant table réutilisable optimisé pour desktop
import React, { useState, useMemo } from 'react';
import { ChevronUp, ChevronDown, Search, Filter, Download, MoreHorizontal } from 'lucide-react';
import { Button, IconButton } from './Button';

export interface Column<T = any> {
  key: string;
  title: string;
  width?: string;
  sortable?: boolean;
  filterable?: boolean;
  render?: (value: any, record: T, index: number) => React.ReactNode;
  className?: string;
  align?: 'left' | 'center' | 'right';
}

export interface TableProps<T = any> {
  columns: Column<T>[];
  data: T[];
  loading?: boolean;
  pagination?: {
    current: number;
    pageSize: number;
    total: number;
    onChange: (page: number, pageSize: number) => void;
  };
  selection?: {
    selectedRowKeys: string[];
    onChange: (selectedRowKeys: string[], selectedRows: T[]) => void;
    getCheckboxProps?: (record: T) => { disabled?: boolean };
  };
  rowKey?: string | ((record: T) => string);
  onRow?: (record: T, index: number) => {
    onClick?: () => void;
    onDoubleClick?: () => void;
    className?: string;
  };
  scroll?: { x?: number; y?: number };
  size?: 'small' | 'middle' | 'large';
  bordered?: boolean;
  showHeader?: boolean;
  title?: () => React.ReactNode;
  footer?: () => React.ReactNode;
  expandable?: {
    expandedRowRender: (record: T, index: number) => React.ReactNode;
    rowExpandable?: (record: T) => boolean;
  };
  className?: string;
}

export const Table = <T extends Record<string, any>>({
  columns,
  data,
  loading = false,
  pagination,
  selection,
  rowKey = 'id',
  onRow,
  scroll,
  size = 'middle',
  bordered = false,
  showHeader = true,
  title,
  footer,
  expandable,
  className = ''
}: TableProps<T>) => {
  const [sortConfig, setSortConfig] = useState<{
    key: string;
    direction: 'asc' | 'desc';
  } | null>(null);
  const [filters, setFilters] = useState<Record<string, string>>({});
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());

  // Tri des données
  const sortedData = useMemo(() => {
    if (!sortConfig) return data;

    return [...data].sort((a, b) => {
      const aValue = a[sortConfig.key];
      const bValue = b[sortConfig.key];

      if (aValue < bValue) {
        return sortConfig.direction === 'asc' ? -1 : 1;
      }
      if (aValue > bValue) {
        return sortConfig.direction === 'asc' ? 1 : -1;
      }
      return 0;
    });
  }, [data, sortConfig]);

  // Filtrage des données
  const filteredData = useMemo(() => {
    return sortedData.filter(record => {
      return Object.entries(filters).every(([key, filterValue]) => {
        if (!filterValue) return true;
        const recordValue = String(record[key]).toLowerCase();
        return recordValue.includes(filterValue.toLowerCase());
      });
    });
  }, [sortedData, filters]);

  // Pagination des données
  const paginatedData = useMemo(() => {
    if (!pagination) return filteredData;
    
    const start = (pagination.current - 1) * pagination.pageSize;
    const end = start + pagination.pageSize;
    return filteredData.slice(start, end);
  }, [filteredData, pagination]);

  const handleSort = (columnKey: string) => {
    let direction: 'asc' | 'desc' = 'asc';
    
    if (sortConfig && sortConfig.key === columnKey && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    
    setSortConfig({ key: columnKey, direction });
  };

  const handleFilter = (columnKey: string, value: string) => {
    setFilters(prev => ({
      ...prev,
      [columnKey]: value
    }));
  };

  const getRowKey = (record: T, index: number): string => {
    if (typeof rowKey === 'function') {
      return rowKey(record);
    }
    return record[rowKey] || index.toString();
  };

  const toggleRowExpansion = (key: string) => {
    const newExpandedRows = new Set(expandedRows);
    if (expandedRows.has(key)) {
      newExpandedRows.delete(key);
    } else {
      newExpandedRows.add(key);
    }
    setExpandedRows(newExpandedRows);
  };

  const sizeClasses = {
    small: 'text-xs',
    middle: 'text-sm',
    large: 'text-base'
  };

  const cellPadding = {
    small: 'px-2 py-1',
    middle: 'px-4 py-2',
    large: 'px-6 py-3'
  };

  if (loading) {
    return (
      <div className="w-full">
        <TableSkeleton />
      </div>
    );
  }

  return (
    <div className={`overflow-hidden ${className}`}>
      {title && (
        <div className="bg-white px-6 py-4 border-b border-gray-200">
          {title()}
        </div>
      )}

      <div className="overflow-x-auto" style={scroll?.x ? { maxWidth: scroll.x } : undefined}>
        <table className={`
          min-w-full divide-y divide-gray-200 ${sizeClasses[size]}
          ${bordered ? 'border border-gray-200' : ''}
        `}>
          {showHeader && (
            <thead className="bg-gray-50">
              <tr>
                {selection && (
                  <th className={`${cellPadding[size]} w-12`}>
                    <input
                      type="checkbox"
                      className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                      onChange={(e) => {
                        const allKeys = paginatedData.map((record, index) => getRowKey(record, index));
                        if (e.target.checked) {
                          selection.onChange(allKeys, paginatedData);
                        } else {
                          selection.onChange([], []);
                        }
                      }}
                      checked={
                        paginatedData.length > 0 && 
                        paginatedData.every((record, index) => 
                          selection.selectedRowKeys.includes(getRowKey(record, index))
                        )
                      }
                    />
                  </th>
                )}
                {expandable && (
                  <th className={`${cellPadding[size]} w-12`}></th>
                )}
                {columns.map((column) => (
                  <th
                    key={column.key}
                    className={`
                      ${cellPadding[size]} text-left text-xs font-medium text-gray-500 uppercase tracking-wider
                      ${column.className || ''}
                      ${column.sortable ? 'cursor-pointer hover:bg-gray-100' : ''}
                    `}
                    style={column.width ? { width: column.width } : undefined}
                    onClick={column.sortable ? () => handleSort(column.key) : undefined}
                  >
                    <div className="flex items-center justify-between">
                      <span>{column.title}</span>
                      <div className="flex items-center space-x-1">
                        {column.sortable && (
                          <div className="flex flex-col">
                            <ChevronUp 
                              className={`h-3 w-3 ${
                                sortConfig?.key === column.key && sortConfig.direction === 'asc'
                                  ? 'text-primary-600' 
                                  : 'text-gray-300'
                              }`} 
                            />
                            <ChevronDown 
                              className={`h-3 w-3 -mt-1 ${
                                sortConfig?.key === column.key && sortConfig.direction === 'desc'
                                  ? 'text-primary-600' 
                                  : 'text-gray-300'
                              }`} 
                            />
                          </div>
                        )}
                        {column.filterable && (
                          <div className="relative">
                            <input
                              type="text"
                              placeholder="Filtrer..."
                              className="w-20 px-2 py-1 text-xs border border-gray-300 rounded"
                              value={filters[column.key] || ''}
                              onChange={(e) => handleFilter(column.key, e.target.value)}
                              onClick={(e) => e.stopPropagation()}
                            />
                          </div>
                        )}
                      </div>
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
          )}
          <tbody className="bg-white divide-y divide-gray-200">
            {paginatedData.map((record, index) => {
              const key = getRowKey(record, index);
              const rowProps = onRow?.(record, index) || {};
              const isExpanded = expandedRows.has(key);
              
              return (
                <React.Fragment key={key}>
                  <tr
                    className={`
                      hover:bg-gray-50 transition-colors
                      ${rowProps.className || ''}
                      ${rowProps.onClick ? 'cursor-pointer' : ''}
                    `}
                    onClick={rowProps.onClick}
                    onDoubleClick={rowProps.onDoubleClick}
                  >
                    {selection && (
                      <td className={cellPadding[size]}>
                        <input
                          type="checkbox"
                          className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                          checked={selection.selectedRowKeys.includes(key)}
                          onChange={(e) => {
                            const newSelectedKeys = e.target.checked
                              ? [...selection.selectedRowKeys, key]
                              : selection.selectedRowKeys.filter(k => k !== key);
                            
                            const newSelectedRows = newSelectedKeys.map(k => 
                              paginatedData.find((r, i) => getRowKey(r, i) === k)
                            ).filter(Boolean) as T[];
                            
                            selection.onChange(newSelectedKeys, newSelectedRows);
                          }}
                          {...(selection.getCheckboxProps?.(record) || {})}
                        />
                      </td>
                    )}
                    {expandable && (
                      <td className={cellPadding[size]}>
                        {expandable.rowExpandable?.(record) !== false && (
                          <button
                            onClick={() => toggleRowExpansion(key)}
                            className="text-gray-400 hover:text-gray-600"
                          >
                            {isExpanded ? (
                              <ChevronUp className="h-4 w-4" />
                            ) : (
                              <ChevronDown className="h-4 w-4" />
                            )}
                          </button>
                        )}
                      </td>
                    )}
                    {columns.map((column) => {
                      const value = record[column.key];
                      const content = column.render ? column.render(value, record, index) : value;
                      
                      return (
                        <td
                          key={column.key}
                          className={`
                            ${cellPadding[size]} whitespace-nowrap
                            ${column.className || ''}
                            ${column.align === 'center' ? 'text-center' : 
                              column.align === 'right' ? 'text-right' : 'text-left'}
                          `}
                        >
                          {content}
                        </td>
                      );
                    })}
                  </tr>
                  {expandable && isExpanded && (
                    <tr>
                      <td 
                        colSpan={
                          columns.length + 
                          (selection ? 1 : 0) + 
                          (expandable ? 1 : 0)
                        }
                        className="px-6 py-4 bg-gray-50"
                      >
                        {expandable.expandedRowRender(record, index)}
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              );
            })}
          </tbody>
        </table>
      </div>

      {footer && (
        <div className="bg-white px-6 py-4 border-t border-gray-200">
          {footer()}
        </div>
      )}

      {pagination && (
        <TablePagination
          current={pagination.current}
          pageSize={pagination.pageSize}
          total={filteredData.length}
          onChange={pagination.onChange}
        />
      )}
    </div>
  );
};

// Composant de pagination
const TablePagination: React.FC<{
  current: number;
  pageSize: number;
  total: number;
  onChange: (page: number, pageSize: number) => void;
}> = ({ current, pageSize, total, onChange }) => {
  const totalPages = Math.ceil(total / pageSize);
  const startIndex = (current - 1) * pageSize + 1;
  const endIndex = Math.min(current * pageSize, total);

  const getPageNumbers = () => {
    const pages = [];
    const maxVisible = 5;
    
    let start = Math.max(1, current - Math.floor(maxVisible / 2));
    let end = Math.min(totalPages, start + maxVisible - 1);
    
    if (end - start + 1 < maxVisible) {
      start = Math.max(1, end - maxVisible + 1);
    }
    
    for (let i = start; i <= end; i++) {
      pages.push(i);
    }
    
    return pages;
  };

  return (
    <div className="bg-white px-6 py-4 flex items-center justify-between border-t border-gray-200">
      <div className="flex items-center text-sm text-gray-700">
        <span>
          Affichage de {startIndex} à {endIndex} sur {total} éléments
        </span>
        <select
          value={pageSize}
          onChange={(e) => onChange(1, Number(e.target.value))}
          className="ml-4 border border-gray-300 rounded px-2 py-1 text-sm"
        >
          <option value={10}>10 / page</option>
          <option value={20}>20 / page</option>
          <option value={50}>50 / page</option>
          <option value={100}>100 / page</option>
        </select>
      </div>
      
      <div className="flex items-center space-x-2">
        <Button
          variant="secondary"
          size="sm"
          disabled={current === 1}
          onClick={() => onChange(current - 1, pageSize)}
        >
          Précédent
        </Button>
        
        {getPageNumbers().map(page => (
          <Button
            key={page}
            variant={page === current ? 'primary' : 'secondary'}
            size="sm"
            onClick={() => onChange(page, pageSize)}
          >
            {page}
          </Button>
        ))}
        
        <Button
          variant="secondary"
          size="sm"
          disabled={current === totalPages}
          onClick={() => onChange(current + 1, pageSize)}
        >
          Suivant
        </Button>
      </div>
    </div>
  );
};

// Skeleton de chargement pour le tableau
const TableSkeleton: React.FC = () => (
  <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 rounded-lg">
    <div className="bg-gray-50 px-6 py-3 border-b border-gray-200">
      <div className="flex space-x-4">
        {[1, 2, 3, 4].map(i => (
          <div key={i} className="h-4 bg-gray-200 rounded animate-pulse flex-1" />
        ))}
      </div>
    </div>
    <div className="bg-white">
      {[1, 2, 3, 4, 5].map(i => (
        <div key={i} className="px-6 py-4 border-b border-gray-200">
          <div className="flex space-x-4">
            {[1, 2, 3, 4].map(j => (
              <div key={j} className="h-4 bg-gray-200 rounded animate-pulse flex-1" />
            ))}
          </div>
        </div>
      ))}
    </div>
  </div>
);